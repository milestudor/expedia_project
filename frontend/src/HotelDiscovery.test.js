import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, afterEach, expect, it, vi } from 'vitest'
import HotelDiscovery from './HotelDiscovery.vue'

const hotels = [
  { place_id: 'first', name: 'Provider Hotel', address: 'Boston', latitude: 42.36, longitude: -71.06 },
  { place_id: 'second', name: null, address: null, latitude: 42.361, longitude: -71.061 },
]
const data = { center: { postcode: '02108', latitude: 42.36, longitude: -71.06 }, hotels, limit: 50 }
const create = () => mount(HotelDiscovery, { global: { stubs: { HotelMap: { name: 'MapStub', props: ['selectedId'], template: '<button class="map-test" @click="$emit(\'select\', \'second\')">Map</button>' } } } })
const response = (body, status = 200) => ({ ok: status === 200, status, json: async () => body })
// Legacy Part 1 checks run after a successful empty local lookup.
const rawStub = vi.stubGlobal.bind(vi)
beforeEach(() => {
  vi.spyOn(vi, 'stubGlobal').mockImplementation((name, mock) => {
    if (name !== 'fetch') return rawStub(name, mock)
    return rawStub(name, (url, options) => {
      if (url.startsWith('/api/local-hotels?postcode=')) return Promise.resolve(response({ hotels: [] }))
      if (url === '/api/local-hotels/status') return Promise.resolve(response({ saved_ids: [] }))
      return options === undefined ? mock(url) : mock(url, options)
    })
  })
})
afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks() })

it('preserves leading zeros, renders honest fields, and synchronizes selections both ways', async () => {
  const fetch = vi.fn().mockResolvedValue(response(data))
  vi.stubGlobal('fetch', fetch)
  const wrapper = create()
  expect(fetch).not.toHaveBeenCalled()
  await wrapper.get('input').setValue(' 02108 ')
  await wrapper.get('form').trigger('submit')
  await flushPromises()
  expect(fetch).toHaveBeenCalledWith('/api/hotels?postcode=02108')
  expect(wrapper.text()).toContain('Hotel name unavailable')
  expect(wrapper.text()).toContain('Address unavailable')
  await wrapper.get('.hotel-card').trigger('click')
  expect(wrapper.get('.hotel-card').attributes('aria-pressed')).toBe('true')
  expect(wrapper.findComponent({ name: 'MapStub' }).props('selectedId')).toBe('first')
  await wrapper.get('.map-test').trigger('click')
  expect(wrapper.findAll('.hotel-card')[1].attributes('aria-pressed')).toBe('true')
})

it.each(['1234', '123456', 'abcde', '１２３４５', ''])('rejects invalid ZIP %s locally', async (zip) => {
  const fetch = vi.fn()
  vi.stubGlobal('fetch', fetch)
  const wrapper = create()
  await wrapper.get('input').setValue(zip)
  await wrapper.get('form').trigger('submit')
  expect(fetch).not.toHaveBeenCalled()
  expect(wrapper.get('[role="alert"]').text()).toContain('Check your ZIP')
})

it.each([[404, 'ZIP code not found'], [502, 'Search unavailable'], [503, 'Search unavailable']])('distinguishes error %s', async (status, heading) => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response({ detail: 'Test response' }, status)))
  const wrapper = create()
  await wrapper.get('input').setValue('02108')
  await wrapper.get('form').trigger('submit')
  await flushPromises()
  expect(wrapper.get('[role="alert"]').text()).toContain(heading)
  expect(wrapper.text()).not.toContain('No nearby hotels returned')
})

it('clears stale results, disables repeat submissions, and distinguishes empty results', async () => {
  let resolve
  const fetch = vi.fn().mockResolvedValueOnce(response(data)).mockImplementationOnce(() => new Promise(done => { resolve = done }))
  vi.stubGlobal('fetch', fetch)
  const wrapper = create()
  await wrapper.get('input').setValue('02108')
  await wrapper.get('form').trigger('submit')
  await flushPromises()
  await wrapper.get('form').trigger('submit')
  expect(wrapper.find('.hotel-card').exists()).toBe(false)
  expect(wrapper.get('button[type="submit"]').element.disabled).toBe(true)
  await wrapper.get('form').trigger('submit')
  expect(fetch).toHaveBeenCalledTimes(2)
  resolve(response({ ...data, hotels: [] }))
  await flushPromises()
  expect(wrapper.text()).toContain('No nearby hotels returned')
  expect(wrapper.find('.map-test').exists()).toBe(true)
})

it('reports network failure', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
  const wrapper = create()
  await wrapper.get('input').setValue('02108')
  await wrapper.get('form').trigger('submit')
  await flushPromises()
  expect(wrapper.get('[role="alert"]').text()).toContain('Check your connection')
})
