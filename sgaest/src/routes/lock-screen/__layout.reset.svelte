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
	let persona = {};
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		cargado = false;
		if (browserGet('refreshToken')) {
			const response = await getCurrentRefresh(fetch, `${variables.BASE_API_URI}/token/refresh`);
			if (response.status >= 400) {
				//window.localStorage.clear();
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
		} else {
			goto('/login');
		}
		cargado = true;
		loading.setLoading(false, 'Cargando, espere por favor...');
	});

	$: {
	}
</script>

<PWA />
<svelte:head>
	<link href="./login/css/style.css" rel="stylesheet" />
	<link href="./login/css/customizer.css" rel="stylesheet" />
</svelte:head>
<GoogleAnalytics />
<Loader />

<!-- [ signin-img ] start -->
{#if cargado}
	<div class="accountbg" />
	<Toast />
	<div class="container d-flex flex-column">
		<div class="row align-items-center justify-content-center g-0 min-vh-100">
			<div class="col-lg-5 col-md-8 py-8 py-xl-0">
				<div class="card shadow">
					<div class="card-body p-6">
						<slot />
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- [ signin-img ] end -->
<style>
	body {
		display: block;
		margin: 8px;
	}

	.accountbg {
		background-image: url('./login/images/auth/img-auth-big.png');
		position: absolute;
		height: 100%;
		width: 100%;
		top: 0;
	}
</style>
