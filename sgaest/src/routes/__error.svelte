<script context="module">
	/** @type {import('@sveltejs/kit').ErrorLoad} */
	export function load({ error, status }) {
		return {
			props: {
				title: `${status}: ${error.message}`
			}
		};
	}
</script>

<script>
	export let title;
</script>

<div class="row align-items-center justify-content-center">
	<!-- Docs -->
	<div class="offset-xl-1 col-xl-4 col-lg-6 col-md-12 col-12 text-center text-lg-start">
		<h3 class="display-1 mb-3">{title}</h3>

		<p class="mb-5 lead">
            ¡UPS! Lo sentimos, no pudimos encontrar la página que estabas buscando. Si cree que esto es un problema con nosotros, <a href="#" class="btn-link">contáctenos</a>
		</p>
		<a href="/" class="btn btn-info me-2">De vuelta al Inicio</a>
	</div>
	<!-- img -->
	<div class="offset-xl-1 col-xl-6 col-lg-6 col-md-12 col-12 mt-8 mt-lg-0">
		<img src="./assets/images/error/404-error-img.svg" alt="" class="w-100" />
	</div>
</div>


