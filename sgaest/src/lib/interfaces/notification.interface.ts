import type { SvelteComponent } from 'svelte'
import type { FlyParams } from 'svelte/types/runtime/transition/index'

export interface NotificacionToast {
    id?: number
    target?: string
    msg?: string
    duration?: number
    initial?: number
    next?: number
    progress?: number
    pausable?: boolean
    dismissable?: boolean
    reversed?: boolean
    intro?: FlyParams
    theme?: { [key: string]: string }
    classes?: string[]
    component?: {
        src: typeof SvelteComponent
        props?: { [key: string]: any }
        sendIdTo?: string
    }
    onpop?(id?: number): any
}


