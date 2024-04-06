<script>
	import { createEventDispatcher, onMount } from 'svelte';
	let item = 1;
	export let ePersona;
	let es_mujer = false;
	const DEBUG = import.meta.env.DEV;

	onMount(async () => {
		console.log(ePersona);
		if (ePersona) {
			if (ePersona.sexo) {
				es_mujer = ePersona.sexo.pk == 1 ?? false;
			}
		}
	});

	const dispatch = createEventDispatcher();

	const actionLoad = (link) => {
		item = link;
		dispatch('actionRun', { action: 'selectItem', data: { item: item } });
	};
	/*
	export let message;*/
</script>

<nav
	class="navbar navbar-expand-md navbar-light mb-4 mb-lg-0 p-0  sidenav h-100 align-items-start "
>
	<!-- Menu -->
	<a class="d-xl-none d-lg-none d-md-none text-inherit fw-bold mt-2" href="#">Menu</a>
	<!-- Button -->
	<button
		class="navbar-toggler d-md-none icon-shape icon-sm rounded bg-primary text-light"
		type="button"
		data-bs-toggle="collapse"
		data-bs-target="#sidenav"
		aria-controls="sidenav"
		aria-expanded="false"
		aria-label="Toggle navigation"
	>
		<span class="fe fe-menu" />
	</button>
	<!-- Collapse navbar -->
	<div class="collapse navbar-collapse" id="sidenav">
		<div class="navbar-nav flex-column m-0 p-0">
			<div class="accordion accordion-flush" id="items">
				<div class="accordion-item mb-2">
					<div class="accordion-header">
						<button
							class="accordion-button accordion-btn-white {[1, 2, 3].includes(item)
								? ''
								: 'collapsed'}"
							type="button"
							style=""
							data-bs-toggle="collapse"
							data-bs-target="#informacionpersonal"
							aria-expanded="true"
						>
							<h4 class="mb-0 texto-blue">Información personal</h4>
						</button>
					</div>
					<div
						id="informacionpersonal"
						class="accordion-collapse {[1, 2, 3].includes(item) ? 'show' : 'collapse'}"
						data-bs-parent="#items"
						aria-expanded="false"
					>
						<div class="accordion-body ">
							<div class="list-group list-group-flush ps-2">
								<a
									href="#datospersonales"
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									1
										? 'active'
										: ''}"
									on:click={() => actionLoad(1)}
									id="menu_element_1"
								>
									Datos personales
									{#if item === 1}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
								<a
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									2
										? 'active'
										: ''}"
									href="#datos-etnia"
									on:click={() => actionLoad(2)}
									id="menu_element_2"
								>
									Datos de étnia/pueblo
									{#if item === 2}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
								<a
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									3
										? 'active'
										: ''}"
									href="#datos-migrante"
									on:click={() => actionLoad(3)}
									id="menu_element_3"
								>
									Datos de extranjero
									{#if item === 3}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
							</div>
						</div>
					</div>
				</div>
				<div class="accordion-item mb-2">
					<div class="accordion-header">
						<button
							class="accordion-button accordion-btn-white {[4, 5, 6].includes(item)
								? ''
								: 'collapsed'}"
							type="button"
							style=""
							data-bs-toggle="collapse"
							data-bs-target="#informacionmedica"
							aria-expanded="true"
						>
							<h4 class="mb-0 texto-blue">Información médica</h4>
						</button>
					</div>
					<div
						id="informacionmedica"
						class="accordion-collapse {[4, 5, 6].includes(item) ? 'show' : 'collapse'}"
						data-bs-parent="#items"
						aria-expanded="false"
					>
						<div class="accordion-body ">
							<div class="list-group list-group-flush ps-2">
								<a
									href="#datosmedicos"
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									4
										? 'active'
										: ''}"
									on:click={() => actionLoad(4)}
									id="menu_element_4"
								>
									Datos médicos
									{#if item === 4}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
								<a
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									5
										? 'active'
										: ''}"
									href="#discapacidad"
									on:click={() => actionLoad(5)}
									id="menu_element_5"
								>
									Discapacidad
									{#if item === 5}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
								{#if es_mujer}
									<a
										class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
										6
											? 'active'
											: ''}"
										href="#embarazo"
										on:click={() => actionLoad(6)}
										id="menu_element_6"
									>
										Embarazo
										{#if item === 6}
											<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
										{/if}
									</a>
								{/if}
							</div>
						</div>
					</div>
				</div>
				<div class="accordion-item mb-2">
					<div class="accordion-header">
						<button
							class="accordion-button accordion-btn-white {[7, 8, 9, 12, 13].includes(item)
								? ''
								: 'collapsed'}"
							type="button"
							style=""
							data-bs-toggle="collapse"
							data-bs-target="#informacionacademica"
							aria-expanded="true"
						>
							<h4 class="mb-0 texto-blue">Información académica</h4>
						</button>
					</div>
					<div
						id="informacionacademica"
						class="accordion-collapse {[7, 8, 9, 12, 13].includes(item) ? 'show' : 'collapse'}"
						data-bs-parent="#items"
						aria-expanded="false"
					>
						<div class="accordion-body ">
							<div class="list-group list-group-flush ps-2">
								<a
									href="#formacionacademica"
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									7
										? 'active'
										: ''}"
									on:click={() => actionLoad(7)}
									id="menu_element_7"
								>
									Formación académica
									{#if item === 7}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
								<a
									href="#capacitaciones"
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									8
										? 'active'
										: ''}"
									on:click={() => actionLoad(8)}
									id="menu_element_8"
								>
									Capacitaciones
									{#if item === 8}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
								<a
									href="#certificaciones"
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									9
										? 'active'
										: ''}"
									on:click={() => actionLoad(9)}
									id="menu_element_9"
								>
									Certificaciones
									{#if item === 9}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
								<a
									href="#proyectos"
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									12
										? 'active'
										: ''}"
									on:click={() => actionLoad(12)}
									id="menu_element_12"
								>
									Proyectos
									{#if item === 12}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
								<a
									href="#becas"
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									13
										? 'active'
										: ''}"
									on:click={() => actionLoad(13)}
									id="menu_element_13"
								>
									Becas
									{#if item === 13}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
							</div>
						</div>
					</div>
				</div>
				<div class="accordion-item mb-2">
					<div class="accordion-header">
						<button
							class="accordion-button accordion-btn-white {[10, 11].includes(item)
								? ''
								: 'collapsed'}"
							type="button"
							style=""
							data-bs-toggle="collapse"
							data-bs-target="#deporte_curltura"
							aria-expanded="true"
						>
							<h4 class="mb-0 texto-blue">Deporte y cultura</h4>
						</button>
					</div>
					<div
						id="deporte_curltura"
						class="accordion-collapse {[10, 11].includes(item) ? 'show' : 'collapse'}"
						data-bs-parent="#items"
						aria-expanded="false"
					>
						<div class="accordion-body ">
							<div class="list-group list-group-flush ps-2">
								<a
									href="#artista"
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									10
										? 'active'
										: ''}"
									on:click={() => actionLoad(10)}
									id="menu_element_10"
								>
									Artista
									{#if item === 10}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
								<a
									href="#deporte"
									class="list-group-item-white pb-2 d-flex justify-content-between align-items-start {item ===
									11
										? 'active'
										: ''}"
									on:click={() => actionLoad(11)}
									id="menu_element_11"
								>
									Deporte de alto rendimiento
									{#if item === 11}
										<i style="color: #fe9900 !important;" class="fe fe-chevron-right m-1" />
									{/if}
								</a>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!--<ul class="list-unstyled mb-0 py-3 pt-md-1 ">
				<li class="mb-1 border-0">
					<a
						class="p-0 d-inline-flex align-items-center rounded pointer fw-bold"
						data-bs-toggle="collapse"
						data-bs-target="#datos-personales"
						aria-expanded="true"
						aria-current="true"
						href="javascript:;"
					>
						Información personal
					</a>

					<div
						class="collapse {[1, 2, 3, 4, 5, 6, 7, 8].includes(item) ? 'show' : ''} mt-2"
						id="datos-personales"
						style=""
					>
						<ul class="list-unstyled fw-normal pb-1 small">
							<li class="nav-item {item === 1 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#datos-personales-basicos"
									on:click={() => actionLoad(1)}
									id="menu_element_1"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Datos básicos
									</div>
								</a>
							</li>
							<li class="nav-item {item === 2 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#datos-personales-nacimiento"
									on:click={() => actionLoad(2)}
									id="menu_element_2"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Datos nacimiento
									</div>
								</a>
							</li>
							<li class="nav-item {item === 3 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#datos-personales-domicilio"
									on:click={() => actionLoad(3)}
									id="menu_element_3"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Datos de domicilio
									</div>
								</a>
							</li>
							<li class="nav-item {item === 4 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#datos-personales-familiares"
									on:click={() => actionLoad(4)}
									id="menu_element_4"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Datos familiares
									</div>
								</a>
							</li>
							<li class="nav-item {item === 5 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#datos-personales-etnia"
									on:click={() => actionLoad(5)}
									id="menu_element_5"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Étnia, pueblo y nacionalidades
									</div>
								</a>
							</li>
							<li class="nav-item {item === 6 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#datos-personales-discapacidad"
									on:click={() => actionLoad(6)}
									id="menu_element_6"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Discapacidad
									</div>
								</a>
							</li>
							<li class="nav-item {item === 7 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#datos-personales-situacion-laboral"
									on:click={() => actionLoad(7)}
									id="menu_element_7"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Situación laboral
									</div>
								</a>
							</li>
							<li class="nav-item {item === 8 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#datos-medicos"
									on:click={() => actionLoad(8)}
									id="menu_element_8"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Datos médicos
									</div>
								</a>
							</li>
						</ul>
					</div>
				</li>
				<li class="my-3 border-top" />
				<li class="mb-1 border-0">
					<a
						class="p-0 d-inline-flex align-items-center rounded pointer fw-bold"
						data-bs-toggle="collapse"
						data-bs-target="#formacion-academica"
						aria-expanded="true"
						aria-current="true"
						href="javascript:;"
					>
						Formación académica
					</a>

					<div
						class="collapse {[9, 10, 11].includes(item) ? 'show' : ''}  mt-2"
						id="formacion-academica"
						style=""
					>
						<ul class="list-unstyled fw-normal pb-1 small">
							<li class="nav-item {item === 9 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#formacion-academica-mis-titulos"
									on:click={() => actionLoad(9)}
									id="menu_element_9"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Mis Titulos
									</div>
								</a>
							</li>
							<li class="nav-item {item === 10 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#formacion-academica-mis-capacitaciones"
									on:click={() => actionLoad(10)}
									id="menu_element_10"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Mis capacitaciones
									</div>
								</a>
							</li>
							<li class="nav-item {item === 11 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#formacion-academica-mis-certificaciones"
									on:click={() => actionLoad(11)}
									id="menu_element_11"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Mis certificaciones
									</div>
								</a>
							</li>
						</ul>
					</div>
				</li>
				<li class="my-3 border-top" />
				<li class="mb-1 border-0">
					<a
						class="p-0 d-inline-flex align-items-center rounded pointer fw-bold"
						data-bs-toggle="collapse"
						data-bs-target="#experiencia"
						aria-expanded="true"
						aria-current="true"
						href="javascript:;"
					>
						Experiencia
					</a>

					<div
						class="collapse {[14, 15, 16].includes(item) ? 'show' : ''}  mt-2"
						id="experiencia"
						style=""
					>
						<ul class="list-unstyled fw-normal pb-1 small">
							<li class="nav-item {item === 14 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#experiencia-mis-titulos"
									on:click={() => actionLoad(14)}
									id="menu_element_14"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Experiencia Laboral
									</div>
								</a>
							</li>
							<li class="nav-item {item === 15 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#experiencia-otros-meritos"
									on:click={() => actionLoad(15)}
									id="menu_element_15"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Otros Meritos
									</div>
								</a>
							</li>
							<li class="nav-item {item === 16 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#experiencia-referencias"
									on:click={() => actionLoad(16)}
									id="menu_element_16"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Referencias
									</div>
								</a>
							</li>
						</ul>
					</div>
				</li>
				<li class="my-3 border-top" />
				<li class="mb-1 border-0">
					<a
						class="p-0 d-inline-flex align-items-center rounded pointer fw-bold"
						data-bs-toggle="collapse"
						data-bs-target="#extranjero"
						aria-expanded="true"
						aria-current="true"
						href="javascript:;"
					>
						Extranjero
					</a>

					<div class="collapse {[17].includes(item) ? 'show' : ''} mt-2" id="extranjero" style="">
						<ul class="list-unstyled fw-normal pb-1 small">
							<li class="nav-item {item === 17 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#extranjero-mis-titulos"
									on:click={() => actionLoad(17)}
									id="menu_element_17"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Direccion en el extranjero
									</div>
								</a>
							</li>
						</ul>
					</div>
				</li>
				<li class="my-3 border-top" />
				<li class="mb-1 border-0">
					<a
						class="p-0 d-inline-flex align-items-center rounded pointer fw-bold"
						data-bs-toggle="collapse"
						data-bs-target="#actividad-extracurricular"
						aria-expanded="true"
						aria-current="true"
						href="javascript:;"
					>
						Actividad Extracurricular
					</a>

					<div
						class="collapse {[18, 19].includes(item) ? 'show' : ''} mt-2"
						id="actividad-extracurricular"
						style=""
					>
						<ul class="list-unstyled fw-normal pb-1 small">
							<li class="nav-item {item === 18 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#actividad-extracurricular-artista"
									on:click={() => actionLoad(18)}
									id="menu_element_18"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Artista
									</div>
								</a>
							</li>
							<li class="nav-item {item === 19 ? 'active' : ''}">
								<a
									class="nav-link d-flex justify-content-between align-items-start"
									href="#actividad-extracurricular-deportista"
									on:click={() => actionLoad(19)}
									id="menu_element_19"
								>
									<div class="me-auto">
										<i class="fe fe-chevron-right nav-icon" />Deportista
									</div>
								</a>
							</li>
						</ul>
					</div>
				</li>
			</ul>-->
		</div>
	</div>
</nav>

<style>
	.navbar-light {
		background-color: #f5f4f8 !important;
	}
	.accordion-flush .accordion-item .accordion-button {
		border-radius: 0;
	}
	button:focus:not(:focus-visible) {
		outline: 0;
	}
	.accordion-btn-white:not(.collapsed) {
		box-shadow: inset 0 -1px 0 #e1e1e1;
		color: #fe9900 !important;
	}
	.accordion-button:focus {
		border-color: #d6eaf8;
		box-shadow: #d6eaf8;
		outline: 0;
		z-index: 3;
	}
	.accordion-button:not(.collapsed) {
		background-color: #d6eaf8;
		box-shadow: inset 0 -1px 0 #d6eaf8;
		color: #012e46;
	}
	.accordion-btn-white {
		background-color: #ffffff !important;
	}
	.accordion-button {
		align-items: center;
		background-color: #d6eaf8;
		border: 0;
		border-top-color: currentcolor;
		border-right-color: currentcolor;
		border-bottom-color: currentcolor;
		border-left-color: currentcolor;
		border-radius: 0;
		color: #5c5776;
		display: flex;
		font-size: 0.875rem;
		overflow-anchor: none;
		padding: 1rem 1.25rem;
		position: relative;
		text-align: left;
		transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out,
			border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out, border-radius 0.15s ease;
		width: 100%;
	}
	.list-group-item-white.active {
		background-color: #ffffff !important;
		color: #1c3247 !important;
		font-weight: bold !important;
		border-color: #f1f1f1 !important;
		z-index: 2 !important;
	}
</style>
