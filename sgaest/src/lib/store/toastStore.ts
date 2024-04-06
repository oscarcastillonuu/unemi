import { writable } from "svelte/store";

import type { Toast } from "$lib/interfaces/toast.interface";

export const toasts = writable<Toast>([]);

export const toggle = (id) => {
  toasts.update((all) => all.filter((t) => t.id !== id))
}

export const addToast = (toast) => {
  // Create a unique ID so we can easily find/remove it
  // if it is dismissible/has a timeout.
  const id = Math.floor(Math.random() * 10000);

  // Setup some sensible defaults for a toast.
  const defaults = {
    id: id,
    type: 'info',
    icon: 'info',
    autohide: true,
    delay: 3600,
    //duration: 5600,
    //fade: true,
    isOpen: true,
    bg: 'bg-light',
    color: '',
    textColor: '',
    toggle: () => toggle(id)
  };

  if (toast.type === 'info') {
    toast['icon'] = 'info';
    toast['textColor'] = 'text-info';
  } else if (toast.type === 'error') {
    toast['icon'] = 'danger';
    toast['textColor'] = 'text-danger';
  } else if (toast.type === 'success') {
    toast['icon'] = 'success';
    toast['textColor'] = 'text-success';
  } else if (toast.type === 'warning') {
    toast['icon'] = 'warning';
    toast['textColor'] = 'text-warning';
  }

  const t = { ...defaults, ...toast }

  toasts.update((all) => [t, ...all])
  if (t.delay) setTimeout(() => dismissToast(id), t.delay);
};

export const dismissToast = (id) => {
  toasts.update((all) => all.filter((t) => t.id !== id));
};