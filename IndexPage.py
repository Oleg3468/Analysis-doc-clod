<template>
  <q-page class="flex flex-center bg-dark text-white q-pa-md">
    <div class="full-width text-center" style="max-width: 600px;">
      <div class="q-mb-xl">
        <h1 class="text-h4 text-weight-bolder q-my-none text-gradient">
          AGREEMENT SCANNER
        </h1>
        <p class="text-subtitle2 text-grey-5 q-mt-sm">
          Smart scanning of user agreements from the screen or gallery
        </p>
      </div>

      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-6">
          <q-btn
            stack
            color="primary"
            class="full-width q-py-lg text-weight-bold"
            icon="photo_camera"
            label="Take photo"
            @click="triggerFileInput('camera')"
            push
          />
        </div>
        <div class="col-6">
          <q-btn
            stack
            color="secondary"
            class="full-width q-py-lg text-weight-bold"
            icon="photo_library"
            label="From gallery"
            @click="triggerFileInput('gallery')"
            push
          />
        </div>
      </div>

      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        :capture="captureMode === 'camera' ? 'environment' : undefined"
        style="display: none;"
        @change="onFileSelected"
      />

      <div class="q-mb-lg">
        <q-input
          v-model="pastedText"
          type="textarea"
          filled
          dark
          rows="3"
          label="...or paste agreement text directly"
          class="text-white"
        />
        <q-btn
          v-if="pastedText.trim()"
          color="primary"
          class="q-mt-sm"
          label="Analyze text"
          icon="search"
          @click="analyzeTextInput"
        />
      </div>

      <div v-if="scanning" class="q-my-xl scanner-box relative-position overflow-hidden border-neon rounded-borders">
        <q-img v-if="selectedImage" :src="selectedImage" style="max-height: 250px; opacity: 0.6;" fit="cover" />
        <div class="laser-bar"></div>
        <div class="absolute-center text-weight-bolder text-h6 text-pink q-py-xs q-px-md text-bg">
          SCANNING AGREEMENT...
        </div>
      </div>

      <div v-if="selectedImage && !scanning" class="q-my-lg text-center">
        <q-img
          :src="selectedImage"
          style="max-height: 250px; border-radius: 8px;"
          fit="contain"
          class="shadow-5"
        />
        <q-btn
          flat
          dense
          color="pink-5"
          icon="delete"
          label="Reset"
          class="q-mt-sm"
          @click="resetAll"
        />
      </div>

      <div v-if="errorMessage" class="q-mt-md text-negative">
        {{ errorMessage }}
      </div>

      <div v-if="analyzed && findings.length > 0" class="text-left q-mt-lg">
        <div class="text-h6 text-weight-bold text-pink-5 q-mb-md flex items-center gap-xs">
          <q-icon name="report_problem" /> Unfavorable clauses found: {{ findings.length }}
        </div>

        <q-card
          v-for="(item, idx) in findings"
          :key="idx"
          flat
          bordered
          :class="item.is_critical ? 'card-critical q-mb-md' : 'card-warning q-mb-md'"
        >
          <q-card-section>
            <q-badge
              :color="item.is_critical ? 'pink-6' : 'amber-9'"
              text-color="black"
              class="text-weight-bold text-uppercase q-mb-sm"
            >
              {{ item.is_critical ? 'Critical threat' : 'Rights limitation' }}
            </q-badge>
            <div class="text-h6 text-weight-bold text-white q-mt-xs">
              {{ item.category }}
            </div>
            <p class="text-caption text-grey-4 q-mt-sm q-mb-md">
              {{ item.description }}
            </p>

            <div class="matched-box q-pa-sm rounded-borders text-mono text-pink-3 q-mb-sm">
              <span class="text-grey-6 text-uppercase text-caption block">Matched clause:</span>
              <span class="scanner-text">{{ item.matched }}</span>
            </div>

            <div class="context-box q-pa-md rounded-borders text-grey-5 text-caption">
              <span class="text-grey-6 text-uppercase text-caption block q-mb-xs">Context in the agreement:</span>
              <div v-html="highlightContext(item.context, item.matched)"></div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div v-if="analyzed && findings.length === 0" class="q-mt-xl text-center success-box q-pa-lg rounded-borders">
        <q-icon name="check_circle" size="64px" color="green-5" />
        <div class="text-h6 text-weight-bold text-green-5 q-mt-sm">All clear!</div>
        <p class="text-body2 text-grey-5 q-mt-xs">
          No risky clauses were found in this agreement.
        </p>
      </div>

    </div>
  </q-page>
</template>

<script>
import { ref } from 'vue'
import { useQuasar } from 'quasar'

// Point this at your deployed backend, e.g. via .env: VITE_API_BASE_URL
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000'

export default {
  name: 'IndexPage',
  setup () {
    const $q = useQuasar()
    const scanning = ref(false)
    const analyzed = ref(false)
    const selectedImage = ref(null)
    const findings = ref([])
    const pastedText = ref('')
    const errorMessage = ref('')
    const fileInput = ref(null)
    const captureMode = ref('gallery')

    const triggerFileInput = (mode) => {
      captureMode.value = mode
      $q.notify({
        message: mode === 'camera' ? 'Opening camera...' : 'Opening gallery...',
        color: mode === 'camera' ? 'primary' : 'secondary',
        icon: mode === 'camera' ? 'camera' : 'photo'
      })
      fileInput.value?.click()
    }

    const onFileSelected = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      selectedImage.value = URL.createObjectURL(file)
      scanning.value = true
      analyzed.value = false
      findings.value = []
      errorMessage.value = ''

      try {
        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch(`${API_BASE_URL}/analyze-image?lang=rus+eng`, {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const errBody = await response.json().catch(() => ({}))
          throw new Error(errBody.detail || `Server error (${response.status})`)
        }

        const data = await response.json()
        findings.value = data.findings || []
        analyzed.value = true
      } catch (err) {
        errorMessage.value = `Failed to analyze image: ${err.message}`
        $q.notify({ message: errorMessage.value, color: 'negative' })
      } finally {
        scanning.value = false
        event.target.value = ''
      }
    }

    const analyzeTextInput = async () => {
      if (!pastedText.value.trim()) return

      scanning.value = true
      analyzed.value = false
      findings.value = []
      errorMessage.value = ''
      selectedImage.value = null

      try {
        const response = await fetch(`${API_BASE_URL}/analyze-text`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: pastedText.value })
        })

        if (!response.ok) {
          const errBody = await response.json().catch(() => ({}))
          throw new Error(errBody.detail || `Server error (${response.status})`)
        }

        const data = await response.json()
        findings.value = data.findings || []
        analyzed.value = true
      } catch (err) {
        errorMessage.value = `Failed to analyze text: ${err.message}`
        $q.notify({ message: errorMessage.value, color: 'negative' })
      } finally {
        scanning.value = false
      }
    }

    const highlightContext = (context, matched) => {
      if (!context || !matched) return context
      const escaped = matched.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')
      const reg = new RegExp(`(${escaped})`, 'gi')
      return context.replace(reg, '<mark class="highlight-text">$1</mark>')
    }

    const resetAll = () => {
      selectedImage.value = null
      scanning.value = false
      analyzed.value = false
      findings.value = []
      pastedText.value = ''
      errorMessage.value = ''
    }

    return {
      scanning,
      analyzed,
      selectedImage,
      findings,
      pastedText,
      errorMessage,
      fileInput,
      captureMode,
      triggerFileInput,
      onFileSelected,
      analyzeTextInput,
      highlightContext,
      resetAll
    }
  }
}
</script>

<style scoped>
.text-gradient {
  background: linear-gradient(90deg, #FF4FD8, #4FF8FF);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.border-neon {
  border: 2px solid #FF4FD8;
  box-shadow: 0 0 20px rgba(255, 79, 216, 0.4);
}
.scanner-box {
  border-radius: 12px;
  height: 250px;
}
.laser-bar {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: #FF4FD8;
  box-shadow: 0 0 15px #FF4FD8, 0 0 30px #FF4FD8;
  animation: laser-sweep 2.5s ease-in-out infinite alternate;
}
@keyframes laser-sweep {
  0% { top: 0%; }
  100% { top: 100%; }
}
.text-bg {
  background: rgba(0, 0, 0, 0.7);
  border-radius: 4px;
  border: 1px solid #FF4FD8;
}
.card-critical {
  background: linear-gradient(180deg, #1d141e, #130a13);
  border: 1px solid #FF4FD8;
  border-radius: 14px;
}
.card-warning {
  background: linear-gradient(180deg, #1f1b13, #151109);
  border: 1px solid #FFA800;
  border-radius: 14px;
}
.matched-box {
  background: rgba(0, 0, 0, 0.4);
  border-left: 4px solid #FF4FD8;
}
.context-box {
  background: #0b0c10;
  border: 1px solid #232936;
}
:deep(.highlight-text) {
  background: rgba(255, 79, 216, 0.3);
  color: #FF4FD8;
  font-weight: bold;
  padding: 2px 4px;
  border-radius: 4px;
}
.success-box {
  background: #0f1c14;
  border: 1px solid #234d31;
}
</style>
