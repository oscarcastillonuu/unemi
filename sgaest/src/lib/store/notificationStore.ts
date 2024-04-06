import { toast } from '@zerodevx/svelte-toast'; //https://github.com/zerodevx/svelte-toast
//import { writable } from 'svelte/store';

import type { NotificacionToast } from '$lib/interfaces/notification.interface';

export const addNotification = (data) => {
    let theme = {}
    if (data.type === 'success') {
        theme = {
            '--toastBackground': '#48BB78',
            '--toastBarBackground': '#2F855A'
        }
    }else if (data.type === 'error'){
        theme = {
            '--toastBackground': '#F56565',
            '--toastBarBackground': '#C53030'
        }
    }else if (data.type === 'warning'){
        theme = {
            '--toastBackground': '#fff3cd',
            '--toastBarBackground': 'rgb(202, 138, 4)',
            '--toastColor': '#424242',
        }
    }
    else if (data.type === 'info'){
        theme = {
            '--toastBackground': '#4299E1',
            '--toastBarBackground': '#2B6CB0'
        }
    }

    // Default options
    const defaults = {
        duration: 4000,       // duration of progress bar tween to the `next` value
        initial: 1,           // initial progress bar value
        next: 0,              // next progress value
        pausable: false,      // pause progress bar tween on mouse hover
        dismissable: true,    // allow dismiss with close button
        reversed: false,      // insert new toast to bottom of stack
        intro: { x: 256 },    // toast intro fly animation settings
        theme: theme,         // css var overrides
        classes: []           // user-defined classes
    };
    const options = <NotificacionToast>({ ...defaults, ...data });
    toast.push(options);
};