<script lang="ts">
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';

	export let aData;
</script>

<li class="list-group-item p-0">
	<!-- Toggle -->
	<a
		class="h4 mb-0 d-flex align-items-center text-inherit text-decoration-none py-3 px-4"
		data-bs-toggle="collapse"
		href="#courseFormacionAcademica"
		role="button"
		aria-expanded="false"
		aria-controls="courseFormacionAcademica"
	>
		<div class="me-auto">
			<!-- Title -->
			Formación Acádemica
			<p class="mb-0 text-muted fs-6 mt-1 fw-normal" />
		</div>
		<!-- Chevron -->
		<span class="chevron-arrow ms-4">
			<i class="fe fe-chevron-down fs-4" />
		</span>
	</a>
	<!-- Row -->
	<!-- Collapse -->
	<div class="collapse" id="courseFormacionAcademica" data-bs-parent="#courseAccordion">
		<!-- List group item -->
		<ul class="list-group list-group-flush">
			{#if aData.profesor.persona.miformacionacademica.length > 0}
				{#each aData.profesor.persona.miformacionacademica as foo}
					<!-- content here -->
					<li class="list-group-item disabled" aria-disabled="true">
						<a
							href="#"
							class="d-flex justify-content-between align-items-center text-inherit text-decoration-none"
						>
							<small>{foo.display}</small>
						</a>
					</li>
				{/each}
			{:else}
				<li class="list-group-item disabled" aria-disabled="true">
					<small>No existen registros</small>
				</li>
			{/if}
		</ul>
	</div>
</li>

<li class="list-group-item p-0">
	<!-- Toggle -->
	<a
		class="h4 mb-0 d-flex align-items-center text-inherit text-decoration-none py-3 px-4"
		data-bs-toggle="collapse"
		href="#courseCapaciotacion"
		role="button"
		aria-expanded="false"
		aria-controls="courseCapaciotacion"
	>
		<div class="me-auto">
			<!-- Title -->
			Capacitaciones
			<p class="mb-0 text-muted fs-6 mt-1 fw-normal" />
		</div>
		<!-- Chevron -->
		<span class="chevron-arrow ms-4">
			<i class="fe fe-chevron-down fs-4" />
		</span>
	</a>
	<!-- Row -->
	<!-- Collapse -->
	<div class="collapse" id="courseCapaciotacion" data-bs-parent="#courseAccordion">
		<!-- List group item -->
		<ul class="list-group list-group-flush">
			{#if aData.profesor.persona.miscapacitaciones.length > 0}
				{#each aData.profesor.persona.miscapacitaciones as foo}
					<!-- content here -->
					<li class="list-group-item disabled" aria-disabled="true">
						<a
							href="#"
							class="d-flex justify-content-between align-items-center text-inherit text-decoration-none"
						>
							<small>{foo.display}</small>
						</a>
					</li>
				{/each}
			{:else}
				<li class="list-group-item disabled" aria-disabled="true">
					<small>No existen registros</small>
				</li>
			{/if}
		</ul>
	</div>
</li>

<li class="list-group-item p-0">
	<!-- Toggle -->
	<a
		class="h4 mb-0 d-flex align-items-center text-inherit text-decoration-none py-3 px-4"
		data-bs-toggle="collapse"
		href="#coursePublicaciones"
		role="button"
		aria-expanded="false"
		aria-controls="coursePublicaciones"
	>
		<div class="me-auto">
			<!-- Title -->
			Publicaciones
			<p class="mb-0 text-muted fs-6 mt-1 fw-normal" />
		</div>
		<!-- Chevron -->
		<span class="chevron-arrow ms-4">
			<i class="fe fe-chevron-down fs-4" />
		</span>
	</a>
	<!-- Row -->
	<!-- Collapse -->
	<div class="collapse" id="coursePublicaciones" data-bs-parent="#courseAccordion">
		<!-- List group item -->
		<ul class="list-group list-group-flush">
			{#if aData.profesor.persona.mispublicaciones.length > 0}
				{#each aData.profesor.persona.mispublicaciones as foo}
					<!-- content here -->
					<li class="list-group-item disabled" aria-disabled="true">
						<a
							href="#"
							class="d-flex justify-content-between align-items-center text-inherit text-decoration-none"
						>
							<small>{foo.display}</small>
						</a>
					</li>
				{/each}
			{:else}
				<li class="list-group-item disabled" aria-disabled="true">
					<small>No existen registros</small>
				</li>
			{/if}
		</ul>
	</div>
</li>
