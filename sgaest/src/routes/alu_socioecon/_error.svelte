<script>
	export let title;
	export let message;
</script>

<div class="row align-items-center justify-content-center">
	<!-- Docs -->
	<div class="offset-xl-1 col-xl-4 col-lg-6 col-md-12 col-12 text-center text-lg-start">
		<h3 class="display-3 mb-3">{title}</h3>

		<p class="mb-5 lead">
			{@html message}
		</p>
		<a href="/" class="btn btn-warning me-2">De vuelta al Inicio</a>
	</div>
	<!-- img -->
	<div class="offset-xl-1 col-xl-6 col-lg-6 col-md-12 col-12 mt-8 mt-lg-0">
		<img src="./assets/images/error/404-error-img.svg" alt="" class="w-100" />
	</div>
</div>
