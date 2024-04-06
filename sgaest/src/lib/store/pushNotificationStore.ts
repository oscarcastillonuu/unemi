import { writable } from "svelte/store";

export const pushNotifications = writable([]);

export const addNotifications = (Notifications) => {
  pushNotifications.update(() => Notifications)
};

