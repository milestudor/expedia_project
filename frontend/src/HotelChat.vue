<script setup>
import { onMounted, ref } from 'vue'
const question = ref('')
const loading = ref(false)
const historyLoading = ref(true)
const result = ref(null)
const error = ref('')
const historyError = ref('')
const conversations = ref([])
const messages = ref([])
const conversationId = ref('')
const truncatedHistory = ref(false)
const storageKey = 'expedia.hotelConversation'
// Presentation only: persisted model text and workflow IDs remain unchanged.
function displayAnswer(text) {
  return String(text || '')
    .replace(/\(ID:\s*`?[a-f0-9]{40,}`?\)/gi, '')
    .replace(/`?[a-f0-9]{40,}`?/gi, '[hotel ID in workflow evidence]')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/^[ \t]*[-*] /gm, '• ')
}
const money = cents => cents === null ? 'Insufficient nightly data' : (cents / 100).toLocaleString('en-US', { style: 'currency', currency: 'USD' })
function remember(id) {
  conversationId.value = id || ''
  try {
    if (id) localStorage.setItem(storageKey, id)
    else localStorage.removeItem(storageKey)
  } catch { /* Backend history remains available when browser storage is disabled. */ }
}
async function read(url) {
  const response = await fetch(url)
  const body = await response.json()
  if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : 'Unable to load conversation history.')
  return body
}
async function loadHistory(id) {
  if (!id) return
  const body = await read(`/api/hotel-chat/conversations/${encodeURIComponent(id)}`)
  messages.value = body.messages
  truncatedHistory.value = body.truncated
  result.value = body.latest_result
  remember(id)
}
async function refreshHistory() {
  historyError.value = ''
  try {
    conversations.value = (await read('/api/hotel-chat/conversations')).conversations
    if (conversationId.value) await loadHistory(conversationId.value)
  } catch (cause) {
    historyError.value = cause instanceof TypeError ? 'Unable to load saved history. Your browser selection is retained.' : cause.message
  }
}
async function selectConversation(event) {
  if (loading.value) return
  historyLoading.value = true
  error.value = ''
  result.value = null
  messages.value = []
  remember(event.target.value)
  await refreshHistory()
  historyLoading.value = false
}
function newConversation() {
  if (loading.value || historyLoading.value) return
  remember('')
  result.value = null
  messages.value = []
  truncatedHistory.value = false
  error.value = ''
  question.value = ''
}
onMounted(async () => {
  try { conversationId.value = localStorage.getItem(storageKey) || '' } catch { /* Optional browser selection. */ }
  await refreshHistory()
  historyLoading.value = false
})
async function ask() {
  if (loading.value || historyLoading.value) return
  error.value = ''
  result.value = null
  loading.value = true
  try {
    const payload = { question: question.value }
    if (conversationId.value) payload.conversation_id = conversationId.value
    const response = await fetch('/api/hotel-chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const body = await response.json()
    if (body.conversation_id) remember(body.conversation_id)
    if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : 'Unable to answer. Check your question and try again.')
    result.value = body
  } catch (cause) {
    error.value = cause instanceof TypeError ? 'Unable to reach the assistant. Please try again.' : cause.message
  } finally {
    await refreshHistory()
    loading.value = false
  }
}
</script>

<template>
  <section
    class="hotel-chat"
    aria-labelledby="chat-heading"
    :aria-busy="loading"
  >
    <h2 id="chat-heading">
      Ask about saved hotels
    </h2>
    <p>Compare local hotels with simulated course rates and room availability. These are not live quotes. This assistant cannot book or change records.</p>
    <div class="conversation-controls">
      <label for="saved-conversation">Saved conversation</label>
      <select
        id="saved-conversation"
        :value="conversationId"
        :disabled="loading || historyLoading"
        @change="selectConversation"
      >
        <option value="">
          New conversation
        </option>
        <option
          v-for="item in conversations"
          :key="item.conversation_id"
          :value="item.conversation_id"
        >
          {{ item.title }}
        </option>
      </select>
      <button
        type="button"
        :disabled="loading || historyLoading"
        @click="newConversation"
      >
        Start new conversation
      </button>
    </div>
    <p
      v-if="historyError"
      role="alert"
    >
      {{ historyError }}
    </p>
    <p
      v-if="historyLoading"
      role="status"
    >
      Loading saved conversation…
    </p>
    <div
      v-if="messages.length"
      class="conversation"
      aria-label="Conversation messages"
    >
      <template
        v-for="message in messages"
        :key="message.message_id"
      >
        <article
          v-if="['user_message', 'assistant_answer', 'error'].includes(message.stage)"
          :class="message.role"
        >
          <strong>{{ message.stage === 'error' ? 'Request error' : message.role === 'user' ? 'You' : 'Assistant' }}</strong>
          <p>{{ message.stage === 'assistant_answer' ? displayAnswer(message.content) : message.content }}</p>
          <small>{{ message.timestamp }}</small>
        </article>
      </template>
    </div>
    <form @submit.prevent="ask">
      <label for="hotel-question">Your hotel question</label>
      <textarea
        id="hotel-question"
        v-model="question"
        required
        minlength="2"
        maxlength="1500"
        rows="3"
        :disabled="loading || historyLoading"
        aria-describedby="question-help"
      />
      <p id="question-help">
        Ask about a dated stay, greet the assistant, or follow up within a conversation. Example: Which saved hotels in ZIP 16802 have one room from October 10 to October 12, 2026, for under $250 total?
      </p>
      <button
        type="submit"
        :disabled="loading || historyLoading"
      >
        {{ loading ? 'Checking saved hotel data…' : 'Ask assistant' }}
      </button>
    </form>
    <p
      v-if="loading"
      role="status"
    >
      Generating a query, checking local records, then preparing an answer…
    </p>
    <p
      v-if="error"
      role="alert"
    >
      {{ error }}
    </p>
    <div
      v-if="result"
      aria-live="polite"
    >
      <h3>Answer</h3>
      <p class="chat-answer">
        {{ displayAnswer(result.answer) }}
      </p>
      <p v-if="result.stay">
        <strong>Interpreted stay:</strong> {{ result.stay.check_in }} to {{ result.stay.check_out }} (checkout excluded), {{ result.stay.rooms }} room(s). Check these dates against your question.
      </p>
      <p v-if="result.mode === 'rag' && result.saved_hotel_count === 0">
        No hotels are currently saved locally. Search a ZIP above and choose Add to Local, then ask again. Saving seeds simulated nightly records; inspect their dates before comparing a stay.
      </p>
      <p v-else-if="result.mode === 'rag' && !result.records.length">
        No matching local records were retrieved. Check the saved ZIP associations, requested dates, budget and room count. This does not prove a hotel has no nightly records.
      </p>
      <p v-if="result.truncated">
        Showing at most 20 hotels. Narrow your question for a more focused comparison.
      </p>
      <ul class="chat-matches">
        <li
          v-for="hotel in result.records"
          :key="hotel.hotel_id"
        >
          <strong>{{ hotel.name || 'Unnamed saved hotel' }}</strong> — {{ money(hotel.total_cost_cents) }} for the requested rooms and stay.
          <p>{{ hotel.recorded_nights }}/{{ hotel.expected_nights }} nights recorded. {{ hotel.available ? 'Rooms available for every night (simulated).' : 'Unavailable or insufficient nightly data.' }}</p>
          <details>
            <summary>Nightly course records</summary><ul>
              <li
                v-for="night in hotel.nightly_records"
                :key="night.stay_date"
              >
                {{ night.stay_date }}: {{ money(night.nightly_rate_cents) }} per room, {{ night.rooms_available }} rooms (simulated).
              </li>
            </ul>
          </details>
        </li>
      </ul>
      <details v-if="result.proposed_sql">
        <summary>Show workflow evidence</summary>
        <p>Model: {{ result.model }} · {{ result.source }} · Simulated course data</p>
        <h4>Question</h4><p>{{ result.question }}</p>
        <h4>Proposed SQL</h4><pre>{{ result.proposed_sql }}</pre>
        <h4>Checked, bounded SQL</h4><pre>{{ result.executed_sql }}</pre>
        <h4>Bound parameters</h4><pre>{{ JSON.stringify(result.parameters, null, 2) }}</pre>
        <h4>Retrieved records sent to the second model request</h4><pre>{{ JSON.stringify(result.records, null, 2) }}</pre>
      </details>
    </div>
    <details
      v-if="messages.length"
      class="saved-trace"
    >
      <summary>Saved conversation trace</summary>
      <p>Conversation ID: {{ conversationId }}</p>
      <p v-if="truncatedHistory">
        Showing the latest 200 trace entries. Older records remain in SQLite.
      </p>
      <article
        v-for="message in messages"
        :key="message.message_id"
      >
        <strong>{{ message.stage }} · {{ message.role }}</strong>
        <p>{{ message.timestamp }} · Message {{ message.message_id }}</p>
        <details><summary>Saved content</summary><pre>{{ message.content }}</pre></details>
        <small>Prompt version: {{ message.prompt_version }}</small>
      </article>
    </details>
  </section>
</template>


<style scoped>
.hotel-chat { max-width: 1100px; margin: 2rem auto; padding: 1.5rem; border: 1px solid #c7d2df; border-radius: 12px; background: white; color: #17314d; }
label { display: block; font-weight: bold; margin-bottom: .5rem; }
select { max-width: 100%; padding: .6rem; font: inherit; border-radius: 6px; }
.conversation article { margin: .8rem 0; padding: 1rem; border-radius: 8px; background: #f0f4f8; }
.conversation article.user { background: #e6f0fa; }
.conversation p { white-space: pre-wrap; overflow-wrap: anywhere; }
.saved-trace article { border-top: 1px solid #c7d2df; padding: .7rem 0; overflow-wrap: anywhere; }
textarea { box-sizing: border-box; width: 100%; font: inherit; padding: .75rem; border: 1px solid #64748b; border-radius: 6px; }
button { margin: .5rem 0; padding: .8rem 1.2rem; font: inherit; font-weight: 600; color: white; background: #17314d; border: 1px solid #17314d; border-radius: 6px; cursor: pointer; }
button:disabled { opacity: .65; cursor: wait; }
.chat-answer { white-space: pre-wrap; overflow-wrap: anywhere; }
.chat-matches { padding-left: 1.5rem; }
.chat-matches > li { margin-bottom: 1rem; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f4f7fb; padding: 1rem; max-height: 400px; overflow: auto; }
summary { cursor: pointer; padding: .5rem 0; }
:focus-visible { outline: 3px solid #1476d4; outline-offset: 3px; }
</style>
