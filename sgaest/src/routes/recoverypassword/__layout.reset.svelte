<script lang="ts">
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';

	import GoogleAnalytics from '$components/GoogleAnalytics/GoogleAnalytics.svelte';
	import Loader from '$components/Loader/Loader.svelte';
	import Toast from '$components/Toast.svelte';
	import PWA from '$components/PWA.svelte';

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
</script>

<PWA />
<GoogleAnalytics />
<Loader />

<Toast />
<div>
	<div class="container d-flex flex-column">
		<div class="row align-items-center justify-content-center g-0 min-vh-100">
			<!-- Docs -->
			<div class="col-lg-5 col-md-8 py-8 py-xl-0">
				<slot />
			</div>
		</div>
	</div>
</div>

<!-- [ signin-img ] end -->
<style>
	body {
		--bs-bg-opacity: 1;
		background-color: #fff !important;
		-webkit-font-smoothing: antialiased;
		-webkit-text-size-adjust: 100%;
		-webkit-tap-highlight-color: rgba(0, 0, 0, 0);
		background-color: var(--bs-body-bg);
		color: var(--bs-body-color);
		font-family: var(--bs-body-font-family);
		font-size: var(--bs-body-font-size);
		font-weight: var(--bs-body-font-weight);
		line-height: var(--bs-body-line-height);
		margin: 0;
		text-align: var(--bs-body-text-align);
	}

	.accountbg {
		background-image: url('./static/login/images/auth/img-auth-big.png');
		position: absolute;
		height: 100%;
		width: 100%;
		top: 0;
	}
</style>
