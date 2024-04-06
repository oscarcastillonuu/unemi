import { writable } from 'svelte/store';

import type { UserResponse } from '$lib/interfaces/user.interface';
//import { browser } from '$app/env';



//const persistedUser = browser && localStorage.getItem('user')
export const userData = writable<UserResponse>({});
/*export const user = writable(persistedUser ? JSON.parse(persistedUser) : '')

if (browser) {
    user.subscribe(u => localStorage.user = u)
}*/