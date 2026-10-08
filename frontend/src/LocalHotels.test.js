import { mount, flushPromises } from '@vue/test-utils'
import { afterEach, expect, it, vi } from 'vitest'
import HotelDiscovery from './HotelDiscovery.vue'
const hotel = { place_id: 'id', name: 'Test Hotel', address: null, latitude: 42, longitude: -71 }
const center = { postcode: '02108', country_code: 'us', latitude: 42, longitude: -71 }
const api = { center, hotels: [hotel], limit: 50 }
const local = { center, hotels: [{ ...hotel, demo_nights: [{ stay_date: '2026-10-10', nightly_rate_cents: 500, rooms_available: 10 }] }] }
const response = (body, status = 200) => ({ ok: status < 300, status, json: async () => body })
const create = () => mount(HotelDiscovery, { global: { stubs: { HotelMap: true } } })
async function search(w) { await w.get('input').setValue('02108'); await w.get('form').trigger('submit'); await flushPromises() }
const button = (w, label) => w.findAll('button').find(b => b.text() === label)
afterEach(() => vi.unstubAllGlobals())
it('reads saved values on fresh mount without provider calls', async () => {
  const fetch = vi.fn().mockResolvedValue(response(local)); vi.stubGlobal('fetch', fetch)
  const w = create(); await search(w)
  expect(fetch).toHaveBeenCalledTimes(1)
  expect(fetch.mock.calls[0][0]).toBe('/api/local-hotels?postcode=02108')
  expect(w.text()).toContain('2026-10-10 · $5.00/night · 10 rooms')
  expect(w.text()).toContain('simulated classroom data')
  expect(button(w, 'Saved locally').element.disabled).toBe(true)
})
it('does not fall back after local failure', async () => {
  const fetch = vi.fn().mockResolvedValue(response({ detail: 'Local storage is unavailable.' }, 503)); vi.stubGlobal('fetch', fetch)
  const w = create(); await search(w)
  expect(fetch).toHaveBeenCalledTimes(1)
  expect(w.get('[role="alert"]').text()).toContain('Local storage is unavailable')
})
it('checks provider IDs after empty local success', async () => {
  const fetch = vi.fn().mockResolvedValueOnce(response({ hotels: [] })).mockResolvedValueOnce(response(api)).mockResolvedValueOnce(response({ saved_ids: ['id'] })); vi.stubGlobal('fetch', fetch)
  const w = create(); await search(w)
  expect(fetch.mock.calls.map(c => c[0])).toEqual(['/api/local-hotels?postcode=02108', '/api/hotels?postcode=02108', '/api/local-hotels/status'])
  expect(w.text()).toContain('API results')
  expect(button(w, 'Saved locally').element.disabled).toBe(true)
})
it('sends original result context, disables pending save, and waits for success', async () => {
  let resolve
  const fetch = vi.fn().mockResolvedValueOnce(response({ hotels: [] })).mockResolvedValueOnce(response(api)).mockResolvedValueOnce(response({ saved_ids: [] })).mockImplementationOnce(() => new Promise(done => { resolve = done })); vi.stubGlobal('fetch', fetch)
  const w = create(); await search(w); await w.get('input').setValue('99999')
  await button(w, 'Add to Local').trigger('click')
  expect(button(w, 'Saving…').element.disabled).toBe(true)
  expect(button(w, 'Remove from Local')).toBeUndefined()
  expect(JSON.parse(fetch.mock.calls[3][1].body)).toEqual({ hotel, center })
  resolve(response({ saved: true })); await flushPromises()
  expect(button(w, 'Saved locally').element.disabled).toBe(true)
  expect(button(w, 'Remove from Local')).toBeTruthy()
  expect(w.find('button button').exists()).toBe(false)
})
it('keeps unsaved state on save failure', async () => {
  const fetch = vi.fn().mockResolvedValueOnce(response({ hotels: [] })).mockResolvedValueOnce(response(api)).mockResolvedValueOnce(response({ saved_ids: [] })).mockResolvedValueOnce(response({ detail: 'Save failed' }, 503)); vi.stubGlobal('fetch', fetch)
  const w = create(); await search(w); await button(w, 'Add to Local').trigger('click'); await flushPromises()
  expect(button(w, 'Add to Local').element.disabled).toBe(false)
  expect(button(w, 'Remove from Local')).toBeUndefined()
  expect(w.get('[role="status"]').text()).toContain('Save failed')
})
it('keeps local hotel on delete failure and removes only after success', async () => {
  const fetch = vi.fn().mockResolvedValueOnce(response(local)).mockResolvedValueOnce(response({ detail: 'Removal failed' }, 503)).mockResolvedValueOnce(response(null, 204)); vi.stubGlobal('fetch', fetch)
  const w = create(); await search(w); await w.get('.hotel-card').trigger('click')
  await button(w, 'Remove from Local').trigger('click'); await flushPromises()
  expect(w.find('.hotel-card').exists()).toBe(true)
  expect(w.get('[role="status"]').text()).toContain('Removal failed')
  await button(w, 'Remove from Local').trigger('click'); await flushPromises()
  expect(w.find('.hotel-card').exists()).toBe(false)
  expect(w.text()).toContain('No saved hotels remain')
  expect(fetch.mock.calls[2]).toEqual(['/api/local-hotels?hotel_id=id', { method: 'DELETE' }])
})
