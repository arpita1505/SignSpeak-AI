import { expect, test } from '@playwright/test'

async function installBrowserMocks(page: import('@playwright/test').Page, modelLoaded = true) {
  await page.addInitScript(({ ready }) => {
    const stopped = { value: false }
    Object.defineProperty(window, '__trackStopped', { get: () => stopped.value })
    const stream = document.createElement('canvas').captureStream()
    const originalTracks = stream.getTracks.bind(stream)
    stream.getTracks = () => originalTracks().map((track) => {
      const originalStop = track.stop.bind(track)
      track.stop = () => { stopped.value = true; originalStop() }
      return track
    })
    Object.defineProperty(navigator, 'mediaDevices', {
      configurable: true,
      value: { getUserMedia: async () => stream },
    })
    Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
      configurable: true,
      value: () => ({ drawImage: () => undefined }),
    })
    HTMLCanvasElement.prototype.toDataURL = () => 'data:image/jpeg;base64,ZmFrZQ=='
    window.fetch = async () => new Response(JSON.stringify({
      status: 'ok', model_loaded: ready, model_version: ready ? 'e2e' : null, database: 'ok',
    }), { status: 200, headers: { 'Content-Type': 'application/json' } })
    class MockWebSocket {
      static OPEN = 1
      static CONNECTING = 0
      readyState = MockWebSocket.CONNECTING
      onopen: (() => void) | null = null
      onmessage: ((event: MessageEvent) => void) | null = null
      onclose: (() => void) | null = null
      onerror: (() => void) | null = null
      sent = 0
      constructor(_url: string) {
        setTimeout(() => { this.readyState = MockWebSocket.OPEN; this.onopen?.() }, 0)
      }
      send() {
        this.sent += 1
        const event = ready
          ? { type: 'prediction', sign: 'A', confidence: 0.94, stable: true, commit: this.sent === 1, hands_detected: 1 }
          : { type: 'model_unavailable', message: 'Model not loaded' }
        setTimeout(() => this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(event) })), 0)
      }
      close() { this.readyState = 3; this.onclose?.() }
    }
    Object.defineProperty(window, 'WebSocket', { configurable: true, value: MockWebSocket })
    Object.defineProperty(window, 'speechSynthesis', {
      configurable: true,
      value: { speaking: false, cancel: () => undefined, speak: (utterance: SpeechSynthesisUtterance) => {
        Object.defineProperty(window, '__spoke', { value: true, configurable: true }); setTimeout(() => utterance.onend?.(new SpeechSynthesisEvent('end', { utterance })), 0)
      } },
    })
    class MockUtterance {
      onend: (() => void) | null = null
      onerror: (() => void) | null = null
      lang = ''; rate = 1; pitch = 1
      constructor(public text: string) {}
    }
    Object.defineProperty(window, 'SpeechSynthesisUtterance', { configurable: true, value: MockUtterance })
  }, { ready: modelLoaded })
}

test('mocked camera, prediction, sentence controls, speech and track cleanup work', async ({ page }) => {
  await installBrowserMocks(page)
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'SignSpeak AI' })).toBeVisible()
  await page.getByRole('button', { name: /Start Camera/ }).click()
  await expect(page.getByText('Connected', { exact: true })).toBeVisible()
  await expect(page.getByText('94%')).toBeVisible()
  await expect(page.getByText('A', { exact: true }).last()).toBeVisible()
  await page.waitForTimeout(350)
  await expect(page.locator('.translation-text')).toHaveText('A')
  await page.getByRole('button', { name: 'Space' }).click()
  await page.getByRole('button', { name: /Delete/ }).click()
  await page.getByRole('button', { name: /Speak/ }).click()
  await expect.poll(() => page.evaluate(() => Boolean((window as unknown as { __spoke?: boolean }).__spoke))).toBe(true)
  await page.getByRole('button', { name: /Clear/ }).click()
  await expect(page.locator('.translation-text')).toContainText('Recognition text')
  await page.getByRole('button', { name: /Stop Camera/ }).click()
  await expect.poll(() => page.evaluate(() => Boolean((window as unknown as { __trackStopped?: boolean }).__trackStopped))).toBe(true)
})

test('model unavailable is explicit', async ({ page }) => {
  await installBrowserMocks(page, false)
  await page.goto('/')
  await expect(page.getByText('Model Not Loaded')).toBeVisible()
  await expect(page.getByText('Model: Not Loaded')).toBeVisible()
})
