import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, expect, it, vi } from 'vitest'
import ZipLookup from './ZipLookup.vue'

const location = { postcode: '16802', locality: 'State College', latitude: 40.8, longitude: -77.86 }
const success = (body = location) => ({ ok: true, json: async () => body })
afterEach(() => vi.unstubAllGlobals())

it('requests only on click, displays the result, and clears it while preventing duplicate requests', async () => {
  let resolve
  const fetch = vi.fn().mockResolvedValueOnce(success()).mockImplementationOnce(() => new Promise((done) => { resolve = done }))
  vi.stubGlobal('fetch', fetch)
  const wrapper = mount(ZipLookup)
  expect(fetch).not.toHaveBeenCalled()
  const button = wrapper.get('button')
  expect(button.text()).toBe('Look up ZIP')
  await wrapper.get('input').setValue('16802')
  await wrapper.get('form').trigger('submit')
  await flushPromises()
  expect(fetch).toHaveBeenCalledWith('/api/demo/zip-location?postcode=16802')
  expect(wrapper.get('dl').text()).toContain('Postcode16802')
  expect(wrapper.get('dl').text()).toContain('LocalityState College')
  expect(wrapper.get('dl').text()).toContain('Latitude40.8')
  expect(wrapper.get('dl').text()).toContain('Longitude-77.86')
  await wrapper.get('form').trigger('submit')
  expect(wrapper.find('dl').exists()).toBe(false)
  expect(wrapper.text()).toContain('Looking up ZIP 16802…')
  expect(button.element.disabled).toBe(true)
  await wrapper.get('form').trigger('submit')
  expect(fetch).toHaveBeenCalledTimes(2)
  resolve({ ok: false, json: async () => ({ detail: 'Location provider request failed.' }) })
  await flushPromises()
  expect(wrapper.get('[role="alert"]').text()).toBe('Location provider request failed.')
  expect(button.element.disabled).toBe(false)
  fetch.mockResolvedValueOnce(success({ ...location, locality: undefined }))
  await wrapper.get('form').trigger('submit')
  expect(wrapper.find('[role="alert"]').exists()).toBe(false)
  await flushPromises()
  expect(wrapper.get('dl').text()).not.toContain('Locality')
})

it('shows a safe connection error and re-enables the button', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network failure')))
  const wrapper = mount(ZipLookup)
  await wrapper.get('input').setValue('16802')
  await wrapper.get('form').trigger('submit')
  await flushPromises()
  expect(wrapper.get('[role="alert"]').text()).toBe('We could not look up the ZIP. Please try again.')
  expect(wrapper.get('button').element.disabled).toBe(false)
})


it('preserves leading zeros and trims the submitted ZIP', async () => {
  const fetch = vi.fn().mockResolvedValue(success({ ...location, postcode: '02108' }))
  vi.stubGlobal('fetch', fetch)
  const wrapper = mount(ZipLookup)
  await wrapper.get('input').setValue(' 02108 ')
  await wrapper.get('form').trigger('submit')
  await flushPromises()
  expect(fetch).toHaveBeenCalledWith('/api/demo/zip-location?postcode=02108')
  expect(wrapper.get('dl').text()).toContain('Postcode02108')
})

it.each(['', '1234', '123456', 'abcde', '１２３４５', '16802-1234'])('rejects invalid ZIP %s without requesting', async (value) => {
  const fetch = vi.fn()
  vi.stubGlobal('fetch', fetch)
  const wrapper = mount(ZipLookup)
  await wrapper.get('input').setValue(value)
  await wrapper.get('form').trigger('submit')
  expect(fetch).not.toHaveBeenCalled()
  expect(wrapper.get('[role="alert"]').text()).toBe('Enter a five-digit U.S. ZIP code.')
})
