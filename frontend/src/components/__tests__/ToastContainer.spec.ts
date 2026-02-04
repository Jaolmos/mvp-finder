import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ToastContainer from '../ToastContainer.vue'
import { useToastStore } from '@/stores/toast'

describe('ToastContainer', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renderiza toasts del store', () => {
    const store = useToastStore()
    store.addToast('success', 'Test message')

    const wrapper = mount(ToastContainer)

    expect(wrapper.text()).toContain('Test message')
  })

  it('aplica clases según tipo success', () => {
    const store = useToastStore()
    store.addToast('success', 'Success message')

    const wrapper = mount(ToastContainer)

    const toastItem = wrapper.find('.toast-item')
    expect(toastItem.classes()).toContain('border-green-500')
    expect(toastItem.classes()).toContain('bg-green-50')
    expect(toastItem.classes()).toContain('text-green-800')
  })

  it('aplica clases según tipo error', () => {
    const store = useToastStore()
    store.addToast('error', 'Error message')

    const wrapper = mount(ToastContainer)

    const toastItem = wrapper.find('.toast-item')
    expect(toastItem.classes()).toContain('border-red-500')
    expect(toastItem.classes()).toContain('bg-red-50')
    expect(toastItem.classes()).toContain('text-red-800')
  })

  it('aplica clases según tipo info', () => {
    const store = useToastStore()
    store.addToast('info', 'Info message')

    const wrapper = mount(ToastContainer)

    const toastItem = wrapper.find('.toast-item')
    expect(toastItem.classes()).toContain('border-blue-500')
    expect(toastItem.classes()).toContain('bg-blue-50')
    expect(toastItem.classes()).toContain('text-blue-800')
  })

  it('aplica clases según tipo warning', () => {
    const store = useToastStore()
    store.addToast('warning', 'Warning message')

    const wrapper = mount(ToastContainer)

    const toastItem = wrapper.find('.toast-item')
    expect(toastItem.classes()).toContain('border-amber-500')
    expect(toastItem.classes()).toContain('bg-amber-50')
    expect(toastItem.classes()).toContain('text-amber-800')
  })

  it('muestra icono correcto por tipo success', () => {
    const store = useToastStore()
    store.addToast('success', 'Success message')

    const wrapper = mount(ToastContainer)

    const icon = wrapper.find('svg')
    expect(icon.exists()).toBe(true)
    // Verificar que hay un svg (icono CheckCircle)
    expect(icon.find('path[d*="9 12l2 2 4-4"]').exists()).toBe(true)
  })

  it('muestra icono correcto por tipo error', () => {
    const store = useToastStore()
    store.addToast('error', 'Error message')

    const wrapper = mount(ToastContainer)

    const icon = wrapper.find('svg')
    expect(icon.exists()).toBe(true)
    // Verificar que hay un svg (icono XCircle)
    expect(icon.find('path[d*="10 14l2-2"]').exists()).toBe(true)
  })

  it('muestra icono correcto por tipo info', () => {
    const store = useToastStore()
    store.addToast('info', 'Info message')

    const wrapper = mount(ToastContainer)

    const icon = wrapper.find('svg')
    expect(icon.exists()).toBe(true)
    // Verificar que hay un svg (icono InformationCircle)
    expect(icon.find('path[d*="13 16h-1v-4h-1"]').exists()).toBe(true)
  })

  it('muestra icono correcto por tipo warning', () => {
    const store = useToastStore()
    store.addToast('warning', 'Warning message')

    const wrapper = mount(ToastContainer)

    const icon = wrapper.find('svg')
    expect(icon.exists()).toBe(true)
    // Verificar que hay un svg (icono ExclamationTriangle)
    expect(icon.find('path[d*="12 9v2"]').exists()).toBe(true)
  })

  it('llama removeToast al hacer click en botón cerrar', async () => {
    const store = useToastStore()
    const id = store.addToast('success', 'Test message')

    const wrapper = mount(ToastContainer)

    expect(store.toasts).toHaveLength(1)

    const closeButton = wrapper.find('button')
    await closeButton.trigger('click')

    expect(store.toasts).toHaveLength(0)
  })

  it('renderiza múltiples toasts', () => {
    const store = useToastStore()
    store.addToast('success', 'Message 1')
    store.addToast('error', 'Message 2')
    store.addToast('info', 'Message 3')

    const wrapper = mount(ToastContainer)

    const toastItems = wrapper.findAll('.toast-item')
    expect(toastItems).toHaveLength(3)
    expect(wrapper.text()).toContain('Message 1')
    expect(wrapper.text()).toContain('Message 2')
    expect(wrapper.text()).toContain('Message 3')
  })
})

// Ejecutar: cd frontend && npm run test -- ToastContainer.spec.ts
