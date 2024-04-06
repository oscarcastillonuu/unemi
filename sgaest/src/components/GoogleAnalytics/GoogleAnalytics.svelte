<script>
	import { page } from '$app/stores';
	$: {
		//console.log("page:", $page.url.href)
		if (typeof gtag !== 'undefined') {
			gtag('config', 'G-MWP31MWNNN', {
				page_path: $page.url.href
			});
		}
	}
</script>
