<script lang="ts">
	import Swal from 'sweetalert2';
	import { userData } from '$lib/store/userStore';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import { fly } from 'svelte/transition';
	import { afterUpdate, onDestroy, onMount } from 'svelte';
	//import '$dist/css/style.min.css';

	import GoogleAnalytics from '$components/GoogleAnalytics/GoogleAnalytics.svelte';
	import Loader from '$components/Loader/Loader.svelte';
	import Toast from '$components/Toast.svelte';
	import PWA from '$components/PWA.svelte';

	import {
		getCurrentUser,
		browserGet,
		browserSet,
		getCurrentRefresh
	} from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import { decodeToken } from '$lib/utils/decodetoken';
	import { goto } from '$app/navigation';

	let cargado = false;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	let images = [
		'./login/images/auth/img-auth-big-1-v2.png',
		'./login/images/auth/img-auth-big-2-v2.png',
		'./login/images/auth/img-auth-big-3-v2.png'
	];

	let backgroundImage = '';
	onMount(async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const randomIndex = Math.floor(Math.random() * images.length);
		backgroundImage = `url('${images[randomIndex]}')`;
		console.log(backgroundImage);
		/*if (window) {
			document.querySelector('.aut-bg-img').style.backgroundImage = `${backgroundImage}`;
		}*/
		cargado = false;
		if (browserGet('refreshToken')) {
			const response = await getCurrentRefresh(fetch, `${variables.BASE_API_URI}/token/refresh`);
			if (response.status >= 400) {
				//window.localStorage.clear();
				goto('/lock-screen');
				cargado = true;
			}
			if (response.ok == true) {
				const json = decodeToken(await response.json());
				browserSet('refreshToken', json['tokens'].refresh);
				browserSet('accessToken', json['tokens'].access);
				browserSet('dataSession', JSON.stringify(json));
				userData.set(json);
				return await goto('/');
			}
		}

		cargado = true;
		loading.setLoading(false, 'Cargando, espere por favor...');
	});
</script>

<PWA />
<svelte:head>
	<link href="./login/css/style.css" rel="stylesheet" />
	<link href="./login/css/customizer.css" rel="stylesheet" />
</svelte:head>
<GoogleAnalytics />
<Loader />

{#if cargado}
	<Toast />

	<div
		class="auth-wrapper align-items-stretch aut-bg-img"
		style="background-image: {backgroundImage} !important; background-size: cover; background-attachment: fixed;
		background-repeat: no-repeat; "
	>
		<div class="flex-grow-1">
			<slot />
		</div>
	</div>
{/if}
<!-- [ signin-img ] end -->
