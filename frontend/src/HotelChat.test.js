import { mount, flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import HotelChat from './HotelChat.vue'
const response = (body, ok = true) => ({ ok, json: async () => body })
const cid = '10000000-0000-0000-0000-000000000001'
const answer = { conversation_id: cid, mode: 'rag', answer: 'MOCK answer grounded in records.', question: 'Hotels October 10–12, 2026?', stay: { check_in: '2026-10-10', check_out: '2026-10-12', rooms: 1 }, records: [], proposed_sql: 'SELECT hotel_id FROM saved_hotels', executed_sql: 'SELECT DISTINCT hotel_id FROM (...) LIMIT 21', model: 'fixture-model', source: 'MOCK MODEL', truncated: false }
const message = (role, content, stage) => ({ message_id: role, role, content, stage, timestamp: '2026-10-06T15:00:00+00:00', prompt_version: 'fixture-version' })
function setup(post) {
  let latest = null
  let history = []
  const fetch = vi.fn(async (url, options) => {
    if (options?.method === 'POST') {
      const result = await post(url, options)
      latest = result.ok ? await result.json() : null
      history = result.ok ? [message('user', answer.question, 'user_message'), message('assistant', latest.answer, 'assistant_answer')] : [message('tool', 'Model quota or rate limit reached.', 'error')]
      return result
    }
    if (url.endsWith('/conversations')) return response({ conversations: latest ? [{ conversation_id: cid, title: answer.question }] : [] })
    return response({ messages: history, latest_result: latest, truncated: false })
  })
  vi.stubGlobal('fetch', fetch)
  return fetch
}
beforeEach(() => localStorage.clear())
afterEach(() => { vi.unstubAllGlobals(); localStorage.clear() })
const send = w => w.get('button[type="submit"]')
async function ask(w, text = answer.question) { await flushPromises(); await w.get('textarea').setValue(text); await w.get('form').trigger('submit'); await flushPromises() }
it('shows loading, prevents duplicate submission, then exposes saved answer and evidence', async () => {
  let finish
  const fetch = setup(() => new Promise(resolve => { finish = resolve }))
  const w = mount(HotelChat); await flushPromises()
  await w.get('textarea').setValue(answer.question); await w.get('form').trigger('submit')
  expect(send(w).element.disabled).toBe(true)
  expect(w.get('[role="status"]').text()).toContain('checking local records')
  await w.get('form').trigger('submit')
  expect(fetch.mock.calls.filter(c => c[1]?.method === 'POST')).toHaveLength(1)
  finish(response(answer)); await flushPromises()
  expect(w.text()).toContain(answer.answer)
  expect(w.text()).toContain('No matching local records')
  expect(w.text()).toContain(answer.proposed_sql)
  expect(w.text()).toContain('Saved conversation trace')
  expect(send(w).element.disabled).toBe(false)
  expect(localStorage.getItem('expedia.hotelConversation')).toBe(cid)
})
it('sends conversation ID for follow-ups and saves failure without fabricating an answer', async () => {
  const post = vi.fn().mockResolvedValueOnce(response(answer)).mockResolvedValueOnce(response({ detail: 'Model quota or rate limit reached.', conversation_id: cid }, false))
  setup(post)
  const w = mount(HotelChat); await ask(w); await ask(w, 'What about October 12?')
  expect(JSON.parse(post.mock.calls[1][1].body)).toEqual({ question: 'What about October 12?', conversation_id: cid })
  expect(w.get('[role="alert"]').text()).toContain('Model quota')
  expect(w.text()).toContain('Request error')
  expect(w.text()).not.toContain(answer.answer)
  expect(send(w).element.disabled).toBe(false)
})
it('shows missing-night data without presenting a complete price or availability', async () => {
  setup(async () => response({ ...answer, records: [{ hotel_id: 'fixture', name: 'Fixture Inn', total_cost_cents: null, recorded_nights: 1, expected_nights: 2, available: 0, nightly_records: [{ stay_date: '2026-10-10', nightly_rate_cents: 0, rooms_available: 0 }] }] }))
  const w = mount(HotelChat); await ask(w)
  expect(w.text()).toContain('Insufficient nightly data')
  expect(w.text()).toContain('1/2 nights recorded')
  expect(w.text()).toContain('$0.00 per room, 0 rooms (simulated)')
  expect(w.text()).not.toContain('Rooms available for every night')
})
it('renders model output as text and handles network errors', async () => {
  const post = vi.fn().mockResolvedValueOnce(response({ ...answer, answer: '<img src=x onerror=alert(1)>' })).mockRejectedValueOnce(new TypeError('network'))
  setup(post)
  const w = mount(HotelChat); await ask(w)
  expect(w.find('img').exists()).toBe(false)
  expect(w.text()).toContain('<img src=x')
  await ask(w); expect(w.get('[role="alert"]').text()).toContain('Unable to reach')
})
it('restores backend conversation after remount and starts a new one without deleting saved history', async () => {
  const fetch = setup(async () => response(answer))
  const first = mount(HotelChat); await ask(first); first.unmount()
  const second = mount(HotelChat); await flushPromises()
  expect(second.text()).toContain('You')
  expect(second.text()).toContain(answer.answer)
  expect(fetch.mock.calls.some(c => c[0].endsWith(cid))).toBe(true)
  await second.get('button[type="button"]').trigger('click')
  expect(second.text()).not.toContain('Saved conversation trace')
  expect(localStorage.getItem('expedia.hotelConversation')).toBeNull()
  expect(fetch.mock.calls.filter(c => c[1]?.method === 'DELETE')).toHaveLength(0)
})
it('displays an ordinary greeting without stay claims', async () => {
  setup(async () => response({ ...answer, mode: 'chat', stay: null, proposed_sql: null, answer: 'Hello! I explain saved hotel course data.' }))
  const w = mount(HotelChat); await ask(w, 'Hi')
  expect(w.text()).toContain('Hello!')
  expect(w.text()).not.toContain('Interpreted stay')
  expect(w.text()).not.toContain('No matching local records')
})
it('shows recoverable history failure instead of an empty-history success', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('network')))
  const w = mount(HotelChat); await flushPromises()
  expect(w.get('[role="alert"]').text()).toContain('Unable to load saved history')
  expect(send(w).element.disabled).toBe(false)
})

it('distinguishes empty storage from a filtered no-match', async () => {
  setup(async () => response({ ...answer, saved_hotel_count: 0 }))
  const w = mount(HotelChat)
  await ask(w)
  expect(w.text()).toContain('No hotels are currently saved locally')
  expect(w.text()).toContain('Add to Local')
  expect(w.text()).not.toContain('No matching local records were retrieved')
})

it('cleans answer formatting while preserving exact workflow identifiers', async () => {
  const id = 'a'.repeat(64)
  setup(async () => response({ ...answer, answer: '**Fixture Inn** (ID: `' + id + '`)\n- **Total:** **$200**', proposed_sql: `SELECT hotel_id FROM saved_hotels WHERE hotel_id='${id}'` }))
  const w = mount(HotelChat)
  await ask(w)
  expect(w.get('.chat-answer').text()).toContain('Fixture Inn')
  expect(w.get('.chat-answer').text()).toContain('Total: $200')
  expect(w.get('.chat-answer').text()).not.toContain('**')
  expect(w.get('.chat-answer').text()).not.toContain(id)
  expect(w.text()).toContain(id)
})
