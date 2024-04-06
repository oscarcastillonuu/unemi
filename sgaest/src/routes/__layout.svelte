
<script lang="ts">
	//import "../app.css";
	import Swal from 'sweetalert2';
	import { userData } from '$lib/store/userStore';
	import { navigating, page } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import { fly } from 'svelte/transition';
	import { afterUpdate, onMount } from 'svelte';
	import { connect as connectWS, stateWS } from '$lib/store/socket';
import {addNotifications} from '$lib/store/pushNotificationStore';
	import GoogleAnalytics from '$components/GoogleAnalytics/GoogleAnalytics.svelte';
	import Header from '$components/Header/Header.svelte';
	import Footer from '$components/Footer/Footer.svelte';
	import Loader from '$components/Loader/Loader.svelte';
	import Toast from '$components/Toast.svelte';
	import PWA from '$components/PWA.svelte';
	import BackToTop from '$components/BackToTop/BackToTop.svelte';
	import Notification from '$components/Notification.svelte';

	import '$dist/css/style.min.css';

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	import { apiPOST, browserGet, logOutUser } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import { goto } from '$app/navigation';
	import { decodeToken } from '$lib/utils/decodetoken';
	import { browser } from '$app/env';
	import { addToast } from '$lib/store/toastStore';
	// import Index from './index.svelte';
	//let page = undefined;
	let messages = [];
	onMount(async () => {
		//const ws = connectWS();
		const ws = await connectWS(undefined);
		//console.log(eNotificaciones);
		
	});
	//$: console.log($stateWS);
	afterUpdate(async () => {
		//console.log('entro');
		if (browserGet('refreshToken')) {
			const ds = browserGet('dataSession');
			userData.set(ds);
		} else {
			window.localStorage.clear();
			return await goto('/login');
		}
	});

	const noti = () => {
		return Swal.fire('Any fool can use a computer');
	};

	let key;
	let keyCode;

	const handleKeydown = (event) => {
		//console.log('event:', event);
		key = event.key;
		//console.log('key:', key);
		keyCode = event.keyCode;
		//console.log('keyCode:', keyCode);
		if (keyCode == 116) {
			const NotyKeyCode = {
				position: 'top-center',
				type: 'info',
				icon: 'info',
				title: 'Acción no permitida',
				text: 'Se ha bloqueado el recargar por tu seguridad',
				showCancelButton: false,
				showConfirmButton: true,
				allowOutsideClick: false,
				confirmButtonColor: '#3085d6',
				confirmButtonText: 'Aceptar',
				timer: 6000
			};
			Swal.fire(NotyKeyCode);
		}
		return;
	};
	let state = null;
	let pathname = $page.url.pathname;

	const pushState = () => {
		history.pushState(state, '', pathname);
	};
	if (browser) {
		pushState();
	}

	const popState = (event) => {
		state = event.state;
		pushState();
	};
	const beforeUnload = (event) => {
		//console.log(event);
		//console.log('event:', event);
		/*const NotyKeyCode = {
			position: 'top-center',
			type: 'info',
			icon: 'info',
			title: 'Acción no permitida',
			text: 'Se ha bloqueado el recargar por tu seguridad',
			showCancelButton: false,
			showConfirmButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			confirmButtonText: 'Aceptar',
			timer: 6000
		};

		await Swal.fire(NotyKeyCode)
			.then((result) => {
				if (result.value) {
					window.location.replace("/");
				}
			})
			.catch((error) => {
				window.location.replace("/");
			});
		event.preventDefault();
		event.returnValue = "Se ha bloqueado el recargar por tu seguridad";

		return "Se ha bloqueado el recargar por tu seguridad";*/
		//return window.location.replace("/");
	};

	$:{
		//console.log($stateWS);
		if ($stateWS.requests.length > 0 ){
			$stateWS.requests.forEach(r => {
				if (r.type === "cargar_ultimas_notificaciones"){
					addNotifications(r.datos);
				}
			});
		}
	}
</script>

<!--<svelte:window
	on:keydown|preventDefault={handleKeydown}
	on:beforeunload|preventDefault={beforeUnload}
	on:popstate={popState}
/>-->
<!--<svelte:window on:keydown|preventDefault={handleKeydown} on:popstate={popState} />-->
<PWA />
<GoogleAnalytics />

<div>
	<Loader />
	<Toast />
	<Header />
	<div class="content" style="padding-top: 15px; padding-bottom: 80px;">
		<div class="container-fluid pt-2 pb-2 p-4">
			<Notification />
			<slot />
		</div>
	</div>
	<BackToTop />
	<Footer />
</div>

<style>
	.content > .container {
		margin: 0;
		padding: 0;
	}
</style>
