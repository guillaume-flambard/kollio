export function useDrawer(breakpoint = '(min-width: 1024px)') {
  const route = useRoute()

  const menuOpen = ref(false)
  const menuToggle = ref<HTMLButtonElement | null>(null)
  const drawer = ref<HTMLElement | null>(null)
  let desktopQuery: MediaQueryList | undefined

  function openMenu() {
    menuOpen.value = true
  }

  function closeMenu(restoreFocus = false) {
    if (!menuOpen.value) return
    menuOpen.value = false
    if (restoreFocus) void nextTick(() => menuToggle.value?.focus())
  }

  function onKeydown(event: KeyboardEvent) {
    if (!menuOpen.value) return
    if (event.key === 'Escape') {
      event.preventDefault()
      closeMenu(true)
      return
    }
    if (event.key !== 'Tab' || !drawer.value) return
    const focusable = drawer.value.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
    )
    if (focusable.length === 0) return
    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault()
      last?.focus()
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault()
      first?.focus()
    }
  }

  function onDesktopChange(event: MediaQueryListEvent) {
    if (event.matches) closeMenu()
  }

  watch(menuOpen, async open => {
    if (!import.meta.client) return
    document.body.style.overflow = open ? 'hidden' : ''
    if (open) {
      await nextTick()
      drawer.value?.focus()
    }
  })

  watch(() => route.fullPath, () => closeMenu())

  onMounted(() => {
    window.addEventListener('keydown', onKeydown)
    desktopQuery = window.matchMedia(breakpoint)
    desktopQuery.addEventListener('change', onDesktopChange)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', onKeydown)
    desktopQuery?.removeEventListener('change', onDesktopChange)
    if (import.meta.client) document.body.style.overflow = ''
  })

  return { menuOpen, menuToggle, drawer, openMenu, closeMenu }
}
