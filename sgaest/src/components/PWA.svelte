<script>
	import website from '$lib/config/website';
	import registerSw from '$lib/config/register';
	import { apiPOST, browserGet, loadNotifications } from '$lib/utils/requestUtils';
	import { onMount } from 'svelte';
	const { themeColor } = website;
	const { description } = website;
	const { keywords } = website;
	const { icons } = website;
	const { splash_screens } = website;
	const { author } = website;
	const { webPush } = website;
	let is_authenticated = false;
	let username = undefined;
	onMount(async () => {
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const user = dataSession['user'];
			if (user != undefined && user.username != undefined) {
				is_authenticated = true;
				username = user.username;
			}
		}
		if (is_authenticated) {
			if ('serviceWorker' in navigator) {
				await registerSw();
				if (navigator.serviceWorker) {
					navigator.serviceWorker.ready.then((registration) => {
						registration.active.postMessage({ type: 'PORT_INITIALIZATION' });
						if ('SyncManager' in window) {
							registration.sync.register('sync-data');
						}
						navigator.serviceWorker.addEventListener('message', async (event) => {
							var data = event.data;
							if (data.action) {
								if (data.action === 'loadNotifications') {
									await loadNotifications();
								}
							}
						});
					});
				}
			}

			/*if ('serviceWorker' in navigator) {
				
				
			}*/
		}
	});

	$: {
		//console.log('isLogged', username);
	}
</script>

<svelte:head>
	<!-- Path to manifest.json -->
	<link rel="manifest" crossorigin="use-credentials" href="./manifest.json" />
	<!-- Favicon -->
	<meta name="msapplication-TileImage" content="/pwalogo/512x512.png" />
	<meta name="theme-color" content={themeColor} />
	<meta name="author" content={author} />
	<meta name="description" content={description} />
	<meta name="keywords" content={keywords} />

	<!-- Add to homescreen for Chrome on Android -->
	<meta name="mobile-web-app-capable" content="yes" />
	<meta name="application-name" content="UNEMI- SGAEstudiante" />

	<!-- Add to homescreen for Safari on iOS -->
	<meta name="apple-mobile-web-app-capable" content="yes" />
	<meta name="apple-mobile-web-app-title" content="UNEMI - SGA/Estudiante" />
	<meta name="apple-mobile-web-app-status-bar-style" content="default" />

	{#each icons as icon}
		<link rel="apple-touch-icon" href={icon.src} sizes={icon.sizes} />
	{/each}

	{#each splash_screens as sc}
		<link rel="apple-touch-startup-image" href={sc.src} media={sc.media} />
	{/each}

	<!-- Tile for Win8 -->
	<meta name="msapplication-TileColor" content="#ffffff" />

	<meta name="msapplication-TileImage" content="./pwalogo/512x512.png" />
	{#if is_authenticated && webPush.can}
		<meta name="vapid-key" content={webPush.vapid_key} />
		<meta name="islogged" content={username} />
	{/if}
</svelte:head>
