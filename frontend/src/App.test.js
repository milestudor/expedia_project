import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App.vue'

afterEach(() => vi.unstubAllGlobals())

describe('city search', () => {
  it('renders returned stays in a clearly labeled table', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{
        trip_id: 'T001', trip_name: 'Boston Harbor Weekend', hotel_name: 'Harbor Lantern Hotel',
        city: 'Boston', check_in: '2026-09-18', check_out: '2026-09-20', nights: 2,
        nightly_rate_usd: '150', stay_price_usd: '300',
      }],
    }))
    const wrapper = mount(App)

    await wrapper.get('#city').setValue('Boston')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(fetch).toHaveBeenCalledWith('/api/stays?city=Boston')
    expect(wrapper.get('h2').text()).toBe('Hotel stays in Boston')
    expect(wrapper.get('table').text()).toContain('Harbor Lantern Hotel')
    expect(wrapper.get('table').text()).toContain('$300')
  })

  it('shows a clear message when no stays match', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [] }))
    const wrapper = mount(App)

    await wrapper.get('#city').setValue('Miami')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('No stays found')
    expect(wrapper.text()).toContain('Miami')
  })

  it('explains that a blank search needs a city', async () => {
    const wrapper = mount(App)
    await wrapper.get('form').trigger('submit')
    expect(wrapper.text()).toContain('Enter a city to search.')
  })
})
