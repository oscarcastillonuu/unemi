<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';

	export const load: Load = async ({ params, fetch }) => {
		return {
			status: 302,
			redirect: '/alu_secretaria'
		};
	};
</script>
