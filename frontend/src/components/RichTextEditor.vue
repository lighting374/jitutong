<template>
  <div class="rich-text-editor">
    <div ref="editorContainer" class="editor-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import Quill from 'quill'
import 'quill/dist/quill.snow.css'

interface Props {
  modelValue?: string
  placeholder?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '请输入内容...',
})

const emit = defineEmits<Emits>()

const editorContainer = ref<HTMLElement | null>(null)
let quill: Quill | null = null

onMounted(() => {
  if (!editorContainer.value) return

  // 初始化 Quill 编辑器
  const editor = new Quill(editorContainer.value, {
    theme: 'snow',
    placeholder: props.placeholder,
    modules: {
      toolbar: [
        [{ header: [1, 2, 3, false] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ list: 'ordered' }, { list: 'bullet' }],
        [{ indent: '-1' }, { indent: '+1' }],
        ['link', 'image'],
        [{ color: [] }, { background: [] }],
        [{ align: [] }],
        ['clean'],
      ],
    },
  })
  quill = editor

  // 设置初始内容
  if (props.modelValue) {
    editor.root.innerHTML = props.modelValue
  }

  // 监听内容变化
  editor.on('text-change', () => {
    const html = editor.root.innerHTML
    emit('update:modelValue', html)
  })
})

onBeforeUnmount(() => {
  if (quill) {
    quill = null
  }
})

// 监听外部值变化
watch(
  () => props.modelValue,
  (newValue) => {
    if (quill && quill.root.innerHTML !== newValue) {
      quill.root.innerHTML = newValue || ''
    }
  },
)

// 暴露方法供父组件调用
defineExpose({
  getContent: () => quill?.root.innerHTML || '',
  setContent: (content: string) => {
    if (quill) {
      quill.root.innerHTML = content
    }
  },
  clear: () => {
    if (quill) {
      quill.setText('')
    }
  },
})
</script>

<style scoped>
.rich-text-editor {
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
}

.editor-container {
  min-height: 300px;
}

:deep(.ql-container) {
  font-family:
    'Inter',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    sans-serif;
  font-size: 1rem;
  min-height: 300px;
}

:deep(.ql-editor) {
  min-height: 300px;
}

:deep(.ql-toolbar) {
  border-top-left-radius: 0.5rem;
  border-top-right-radius: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

:deep(.ql-container) {
  border-bottom-left-radius: 0.5rem;
  border-bottom-right-radius: 0.5rem;
}

:deep(.ql-editor.ql-blank::before) {
  font-style: normal;
  color: #9ca3af;
}
</style>
