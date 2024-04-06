import type { Variables } from '$lib/interfaces/variables.interface';
const DEBUG: boolean = import.meta.env.DEV ?
	true :
	false;
	
const BASE_API_URI: string = import.meta.env.DEV ?
	import.meta.env.VITE_BASE_API_URI_DEV :
	import.meta.env.VITE_BASE_API_URI_PROD;

const BASE_API_STATIC: string = import.meta.env.DEV ?
	import.meta.env.VITE_BASE_API_STATIC_DEV :
	import.meta.env.VITE_BASE_API_STATIC_PROD;

const BASE_API: string = import.meta.env.DEV ?
	import.meta.env.VITE_BASE_API_DEV :
	import.meta.env.VITE_BASE_API_PROD;

const BASE_WS: string = import.meta.env.DEV ?
	import.meta.env.VITE_BASE_WS_DEV :
	import.meta.env.VITE_BASE_WS_PROD;

export const variables: Variables = { BASE_API_URI: BASE_API_URI, BASE_API_STATIC: BASE_API_STATIC, BASE_API: BASE_API, BASE_WS: BASE_WS, DEBUG: DEBUG };