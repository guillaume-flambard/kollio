<script setup lang="ts">
import type { IdeaResponse } from '@kollio/api-client'

definePageMeta({ layout: 'workspace', middleware: 'authenticated' })

const { t } = useI18n()
const requestFetch = useRequestFetch()
const localePath = useLocalePath()

const title = ref('')
const pitch = ref('')
const lang = ref('')
const initiativeType = ref('idea')
const submitting = ref(false)
const submitError = ref(false)
const deposited = ref<IdeaResponse>()
const analysisPolls = ref(0)

const typeOptions = useInitiativeTypeOptions()

const canSubmit = computed(() => title.value.trim().length > 0 && pitch.value.trim().length > 0)

const pollTimer = ref<ReturnType<typeof setInterval>>()

const analysisState = computed(() => deposited.value?.analysis?.state ?? 'running')

async function deposit() {
  if (canSubmit.value === false || submitting.value) return
  submitting.value = true
  submitError.value = false
  try {
    const workspaces = await requestFetch<Array<{ id: string }>>('/api/workspaces')
    const workspaceId = workspaces[0]?.id
    if (!workspaceId) throw new Error('no workspace')
    deposited.value = await requestFetch<IdeaResponse>(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/ideas`,
      {
        method: 'POST',
        body: {
          title: title.value.trim(),
          pitch: pitch.value.trim(),
          lang: lang.value || undefined,
          initiative_type: initiativeType.value,
        },
      },
    )
    pollAnalysis()
  }
  catch {
    submitError.value = true
  }
  finally {
    submitting.value = false
  }
}

const analysisResolved = computed(() => analysisState.value !== 'running')

function pollAnalysis() {
  const ideaId = deposited.value?.id
  if (!ideaId) return
  pollTimer.value = setInterval(async () => {
    analysisPolls.value += 1
    if (analysisPolls.value > 20) {
      stopPolling()
      return
    }
    try {
      const refreshed = await requestFetch<IdeaResponse>(`/api/ideas/${encodeURIComponent(ideaId)}`)
      deposited.value = refreshed
      if (analysisResolved.value) stopPolling()
    }
    catch {
      stopPolling()
    }
  }, 400)
}

function stopPolling() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = undefined
  }
}

onUnmounted(stopPolling)

const constraints = computed(() => Object.entries(deposited.value?.analysis?.constraints ?? {}))
const contradictions = computed(() => deposited.value?.analysis?.contradictions ?? [])
const constraintLabels: Record<string, string> = {
  concurrence: 'ideas.deposit.constraints.concurrence',
  cout: 'ideas.deposit.constraints.cout',
  temps: 'ideas.deposit.constraints.temps',
  defendabilite: 'ideas.deposit.constraints.defendabilite',
  acquisition: 'ideas.deposit.constraints.acquisition',
}
</script>

<template>
  <div class="deposit-shell">
      <header class="deposit-header">
        <h1>{{ t('ideas.deposit.title') }}</h1>
        <p>{{ t('ideas.deposit.description') }}</p>
      </header>
      <form v-if="!deposited" class="deposit-form" @submit.prevent="deposit">
        <label class="deposit-field">
          <span>{{ t('ideas.deposit.titleLabel') }}</span>
          <input v-model="title" type="text" :required="true" name="title">
        </label>
        <label class="deposit-field">
          <span>{{ t('ideas.deposit.pitchLabel') }}</span>
          <textarea v-model="pitch" rows="6" :required="true" name="pitch" />
        </label>
        <label class="deposit-field">
          <span>{{ t('ideas.deposit.langLabel') }}</span>
          <select v-model="lang" name="lang">
            <option value="">{{ t('ideas.deposit.langAuto') }}</option>
            <option value="fr">{{ t('ideas.deposit.langFr') }}</option>
            <option value="en">{{ t('ideas.deposit.langEn') }}</option>
          </select>
        </label>
        <label class="deposit-field">
          <span>{{ t('ideas.initiativeTypeLabel') }}</span>
          <select v-model="initiativeType" name="initiative-type">
            <option v-for="(label, value) in typeOptions" :key="value" :value="value">{{ label }}</option>
          </select>
        </label>
        <p v-if="submitError" class="deposit-error" role="alert">{{ t('ideas.deposit.error') }}</p>
        <button type="submit" class="deposit-submit" :disabled="submitting || !canSubmit">
          {{ submitting ? t('ideas.deposit.submitting') : t('ideas.deposit.submit') }}
        </button>
      </form>

      <section v-else class="deposit-verdict" aria-live="polite">
        <KollioAnalysisNarration v-if="analysisState === 'running'" />
        <template v-else>
          <h2>{{ analysisState === 'abstained' ? t('ideas.deposit.abstainedTitle') : t('ideas.deposit.resolvedTitle') }}</h2>
          <p v-if="analysisState === 'abstained'" class="deposit-abstained">
            {{ t('ideas.deposit.abstainedBody') }}
          </p>
          <p v-else class="deposit-score">
            {{ deposited?.analysis?.realism_score }}
          </p>
          <dl class="deposit-constraints">
            <div v-for="[key, dimension] in constraints" :key="key" class="deposit-constraint">
              <dt>{{ t(constraintLabels[key] ?? key) }}</dt>
              <dd>{{ dimension.score ?? '—' }}</dd>
              <p v-if="dimension.basis" class="deposit-basis">
                {{ t(`ideas.analysis.basis.${dimension.basis}`) }}
              </p>
              <p v-if="dimension.gap" class="deposit-gap">
                {{ t('ideas.analysis.gapLine', { gap: dimension.gap }) }}
              </p>
              <p>{{ dimension.note }}</p>
            </div>
          </dl>
          <section v-if="contradictions.length" class="deposit-contradictions">
            <h3>{{ t('ideas.analysis.contradictionsTitle') }}</h3>
            <ul>
              <li v-for="item in contradictions" :key="`${item.target}-${item.ref_id}`">
                <strong>{{ t(`ideas.analysis.contradictionTarget.${item.target}`) }}</strong>
                <span>{{ item.detail }}</span>
              </li>
            </ul>
          </section>
          <NuxtLink class="deposit-open" :to="localePath({ name: 'workspace-ideas-ideaId', params: { ideaId: deposited?.id } })">
            {{ t('ideas.deposit.openIdea') }}
          </NuxtLink>
        </template>
      </section>
    </div>
</template>

<style scoped>
.deposit-shell { display: grid; gap: 22px; max-width: 560px; margin: 0 auto; padding: 22px 4px; }
.deposit-header h1 { margin: 0; font-size: 1.5rem; }
.deposit-header p { margin: 4px 0 0; font-size: .9rem; }
.deposit-form { display: grid; gap: 14px; }
.deposit-field { display: grid; gap: 8px; font-size: .875rem; font-weight: 500; }
.deposit-field input, .deposit-field textarea, .deposit-field select {
  border: 1px solid var(--ui-border); border-radius: 12px; padding: 10px 14px;
  font: inherit; background: var(--ui-bg-elevated); color: var(--ui-text);
}
.deposit-submit {
  justify-self: start; border: 0; border-radius: 12px; padding: 12px 22px; cursor: pointer;
  background: var(--kollio-heading); color: white; font-weight: 570;
}
.deposit-submit:disabled { opacity: .55; cursor: not-allowed; }
.deposit-error { color: var(--ui-error); font-size: .875rem; }
.deposit-verdict { display: grid; gap: 14px; }
.deposit-score { font-size: 2rem; font-weight: 700; }
.deposit-constraints { display: grid; gap: 10px; margin: 0; }
.deposit-constraint { display: grid; gap: 4px; }
.deposit-constraint dd { margin: 0; font-size: .875rem; font-weight: 600; }
.deposit-constraint p { margin: 0; font-size: .8rem; }
.deposit-basis { font-size: .78rem; color: var(--ui-text-muted); text-transform: uppercase; letter-spacing: .06em; }
.deposit-gap { font-size: .8rem; color: var(--ui-text-muted); }
.deposit-contradictions { margin-top: 18px; }
.deposit-contradictions ul { display: grid; gap: 6px; margin: 8px 0 0; padding: 0; list-style: none; }
.deposit-contradictions li { display: flex; gap: 8px; font-size: .875rem; }
.deposit-open { color: var(--kollio-heading); font-weight: 570; }
</style>
