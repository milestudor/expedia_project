import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App.vue'

const stay = {
  trip_id: 'T001', trip_name: 'Boston Harbor Weekend', hotel_name: 'Harbor Lantern Hotel',
  city: 'Boston', state: 'MA', check_in: '2026-09-18', check_out: '2026-09-20', nights: 2,
  nightly_rate_usd: '150', stay_price_usd: '300',
}
const booking = {
  booking_id: 'B004', user_id: 'U001', user_name: 'Alex Morgan', trip_id: 'T001',
  trip_name: stay.trip_name, hotel_name: stay.hotel_name, city: 'Boston',
  check_in: stay.check_in, check_out: stay.check_out, total_price_usd: '300', status: 'confirmed',
}

function mockApi({ searchResults = [stay], history = [] } = {}) {
  return vi.fn(async (url, options = {}) => {
    let body = []
    let status = 200
    if (url === '/api/users') body = [{ user_id: 'U001', name: 'Alex Morgan', email: 'alex@example.com' }]
    if (url === '/api/bookings') body = options.method === 'POST' ? booking : history
    if (url.startsWith('/api/stays')) body = searchResults
    if (url.startsWith('/api/bookings/') && options.method === 'PATCH') body = { ...booking, status: 'cancelled' }
    if (url.startsWith('/api/bookings/') && options.method === 'DELETE') status = 204
    return { ok: true, status, json: async () => body }
  })
}

afterEach(() => vi.unstubAllGlobals())

describe('Expedia Lite booking flow', () => {
  it('searches by hotel name and renders available stays', async () => {
    const fetch = mockApi()
    vi.stubGlobal('fetch', fetch)
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('#query').setValue('Harbor Lantern')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(fetch).toHaveBeenCalledWith('/api/stays?q=Harbor%20Lantern', undefined)
    expect(wrapper.get('table').text()).toContain('Harbor Lantern Hotel')
    expect(wrapper.get('table').text()).toContain('$300')
  })

  it('creates a booking through the results table', async () => {
    const fetch = mockApi()
    vi.stubGlobal('fetch', fetch)
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('#query').setValue('Boston')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    await wrapper.get('button.primary').trigger('click')
    await flushPromises()
    expect(fetch).toHaveBeenCalledWith('/api/bookings', expect.objectContaining({ method: 'POST' }))
    expect(wrapper.text()).toContain('Booking B004 confirmed')
  })

  it('cancels and deletes bookings from history', async () => {
    const fetch = mockApi({ history: [booking] })
    vi.stubGlobal('fetch', fetch)
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('button.secondary').trigger('click')
    await flushPromises()
    expect(fetch).toHaveBeenCalledWith('/api/bookings/B004', expect.objectContaining({ method: 'PATCH' }))
    await wrapper.get('button.danger').trigger('click')
    await flushPromises()
    expect(fetch).toHaveBeenCalledWith('/api/bookings/B004', { method: 'DELETE' })
  })

  it('shows clear blank-search and no-results messages', async () => {
    vi.stubGlobal('fetch', mockApi({ searchResults: [] }))
    const wrapper = mount(App)
    await flushPromises()
    await wrapper.get('form').trigger('submit')
    expect(wrapper.text()).toContain('Enter a hotel name or city')
    await wrapper.get('#query').setValue('No Such Hotel')
    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('No stays found')
  })
})
