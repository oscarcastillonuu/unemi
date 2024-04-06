<script>
	import { createEventDispatcher } from 'svelte';
	let item = 1;

	const dispatch = createEventDispatcher();

	const actionLoad = (link) => {
		item = link;
		dispatch('actionRun', { action: 'selectItem', data: { item: item } });
	};
	/*
	export let message;*/
</script>

<nav class="navbar navbar-expand-md navbar-light shadow-sm mb-4 mb-lg-0 sidenav">
	<!-- Menu -->
	<a class="d-xl-none d-lg-none d-md-none text-inherit fw-bold" href="#">Menu</a>
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
		<div class="navbar-nav flex-column">
			<!--<span class="navbar-header">Subscription</span>-->
			<ul class="list-unstyled ms-n2 mb-4">
				<li class="nav-item {item === 1 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#datos-personales"
						on:click={() => actionLoad(1)}
						id="menu_element_1"
					>
						<div class="me-auto">
							<i class="fe fe-user nav-icon" />Datos personales
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 16 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#datos-etnia"
						on:click={() => actionLoad(16)}
						id="menu_element_16"
					>
						<div class="me-auto">
							<i class="fe fe-user nav-icon" />Datos étnia/pueblo
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 2 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#datos-familiares"
						on:click={() => actionLoad(2)}
						id="menu_element_2"
					>
						<div class="me-auto">
							<i class="fe fe-users nav-icon" />Datos familiares
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 3 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#datos-discapacidad"
						on:click={() => actionLoad(3)}
						id="menu_element_3"
					>
						<div class="me-auto">
							<i class="fe fe-users nav-icon" />Discapacidad
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 4 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#datos-nacimiento"
						on:click={() => actionLoad(4)}
						id="menu_element_4"
					>
						<div class="me-auto">
							<i class="fe fe-calendar nav-icon" />Datos de nacimiento
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 5 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#datos-domicilio"
						on:click={() => actionLoad(5)}
						id="menu_element_5"
					>
						<div class="me-auto">
							<i class="fe fe-clipboard nav-icon" />Datos de domiclio
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 6 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#estructura-familiar"
						on:click={() => actionLoad(6)}
						id="menu_element_6"
					>
						<div class="me-auto">
							<i class="fe fe-clipboard nav-icon" />Estructura familiar
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 7 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#nivel-educacion"
						on:click={() => actionLoad(7)}
						id="menu_element_7"
					>
						<div class="me-auto">
							<i class="fe fe-help-circle nav-icon" />Nivel de educación
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 8 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#caracteristicas-vivienda"
						on:click={() => actionLoad(8)}
						id="menu_element_8"
					>
						<div class="me-auto">
							<i class="fe fe-help-circle nav-icon" />Características de la vivienda
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 9 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#habitos-consumo"
						on:click={() => actionLoad(9)}
						id="menu_element_9"
					>
						<div class="me-auto">
							<i class="fe fe-help-circle nav-icon" />Hábitos de consumo
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 10 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#posesion-bienes"
						on:click={() => actionLoad(10)}
						id="menu_element_10"
					>
						<div class="me-auto">
							<i class="fe fe-help-circle nav-icon" />Posesión de bienes
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 11 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#acceso-tecnologia"
						on:click={() => actionLoad(11)}
						id="menu_element_11"
					>
						<div class="me-auto">
							<i class="fe fe-help-circle nav-icon" />Acceso a tecnología
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 12 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#instalaciones"
						on:click={() => actionLoad(12)}
						id="menu_element_12"
					>
						<div class="me-auto">
							<i class="fe fe-help-circle nav-icon" />Instalaciones
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 13 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#actividades-extracurriculares"
						on:click={() => actionLoad(13)}
						id="menu_element_13"
					>
						<div class="me-auto">
							<i class="fe fe-help-circle nav-icon" />Actividades extracurriculares
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 14 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#recursos-estudio"
						on:click={() => actionLoad(14)}
						id="menu_element_14"
					>
						<div class="me-auto">
							<i class="fe fe-help-circle nav-icon" />Recursos para el estudio
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
				<li class="nav-item {item === 15 ? 'active' : ''}">
					<a
						class="nav-link d-flex justify-content-between align-items-start"
						href="#salud-estudiante"
						on:click={() => actionLoad(15)}
						id="menu_element_15"
					>
						<div class="me-auto">
							<i class="fe fe-help-circle nav-icon" />Salud del estudiante
						</div>
						<!--<span class="badge"><i class="fe fe-info text-warning" /></span>-->
					</a>
				</li>
			</ul>
		</div>
	</div>
</nav>
