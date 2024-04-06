<script lang="ts">
	export let aData;
	import type { Load } from '@sveltejs/kit';
	import { browserGet, apiPOST, apiPOSTFormData, apiGET } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import Swal from 'sweetalert2';
	import { addToast } from '$lib/store/toastStore';
	import { addNotification } from '$lib/store/notificationStore';
	import { loading } from '$lib/store/loadingStore';
	import { Badge, Button, Form, FormGroup, FormText, Input, Label } from 'sveltestrap';
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	const dispatch = createEventDispatcher();
	
	const asignar_grupo_complexivo = async (id_grupo, id_tema) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/tematitulacion_posgrado', {
			id_tema: id_tema,
			id_grupo: id_grupo,
			action: 'asignar_cupo_grupo_complexivo'
		});
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				loading.setLoading(false, 'Cargando, espere por favor...');
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
			}
		}
	};
	const cambiar_grupo_complexivo = async (id_grupo, id_tema, id_grupo_anterior) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/tematitulacion_posgrado', {
			id_grupo_anterior: id_grupo_anterior,
			id_tema: id_tema,
			id_grupo: id_grupo,
			action: 'editar_cupo_grupo_complexivo'
		});
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				loading.setLoading(false, 'Cargando, espere por favor...');
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
			}
		}
	};

	onMount(async () => {});
</script>

<div class="row">
	<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
		<thead class="table-ligth">
			<tr>
				<th scope="col" class="border-top-0 text-center align-middle ">N°</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Grupo</th>
				<th scope="col" class="border-top-0 text-center align-middle " />
			</tr>
		</thead>
		<tbody>
			{#each aData.grupos as grupo, index}
				<tr>
					<td scope="col" class="fs-6 align-middle border-top-0 text-justify text-wrap">
						{index + 1}
					</td>

					<td scope="col" class="fs-6 align-middle border-top-0 text-justify text-wrap">
						<div class="row">
							<div class="col-auto">
								<div class="avatar avatar-md avatar-indicators avatar-offline">
									{#if grupo.tutor.persona.obtenerfoto}
										<!-- content here -->
										<img
											src="{variables.BASE_API}{grupo.tutor.persona.obtenerfoto.foto}"
											class="rounded-circle avatar-xl mb-3"
											alt=""
										/>
									{:else if grupo.tutor.persona.sexo == 1}
										<!-- content here -->
										<img
											src="{variables.BASE_API_STATIC}/images/iconos/mujer.png"
											class="rounded-circle avatar-xl mb-3"
											alt=""
										/>
									{:else}
										<!-- else content here -->
										<img
											src="{variables.BASE_API_STATIC}/images/iconos/hombre.png"
											class="rounded-circle avatar-xl mb-3"
											alt=""
										/>
									{/if}
								</div>
							</div>
							<div class="col ms-n4">
								<h4 class="mb-0 h5">
									{grupo.tutor.display}
								</h4>

								<span class="me-2 fs-6">
									{#each grupo.tutor.persona.lista_emails as item}
										{item}
									{:else}
										No tiene correos
									{/each}
								</span>
								<div class="col ms-n2">
									{#if aData.grupo_seleccionado.length > 0}
										{#if aData.grupo_seleccionado.grupoTitulacionPostgrado.id == grupo.id}<br />
											<span class="badge bg-success btn-xs ">SELECCIONADO</span>
										{/if}
									{/if}
								</div>
							</div>
							<div class="col ms-n2">
								<span class="me-2 fs-6">
									<span class="text-dark  me-1 fw-semi-bold">Cupos disponibles:</span
									>{grupo.cuposdisponibles} / {grupo.cupo}
								</span>
								<br />
								<span class="me-2 fs-6">
									<span class="text-dark  me-1 fw-semi-bold"> Fecha:</span>
									{grupo.fecha} -
									<span class="text-dark  me-1 fw-semi-bold"> Hora:</span>
									{grupo.hora}
								</span>

								<br />
								<span class="fs-6">
									<span class="text-dark  me-1 fw-semi-bold">Url Zoom:</span>
									<a target="_blank" href={grupo.link_zoom}>{grupo.link_zoom}</a>
								</span>
								<br />
								<span class="me-2 fs-6">
									<span class="text-dark  me-1 fw-semi-bold "> Paralelo:</span>
									<span class="text-uppercase">{grupo.paralelo}</span>
								</span>
								<br />
								<span class="me-2 fs-6">
									{#if grupo.itinerariomallaespecilidad}
										<span class="text-dark  me-1 fw-semi-bold "> Mención:</span>
										<span class="text-uppercase">{grupo.itinerariomallaespecilidad.display}</span>
									{/if}
								</span>
							</div>
						</div>
					</td>

					<td scope="col" class="fs-6 align-middle border-top-0 text-center text-wrap">
						{#if grupo.puedeelejirgrupo}
							{#if grupo.cuposdisponibles > 0}
								{#if !aData.se_encuentra_inscrito}
									<button 
										on:click={() =>
										asignar_grupo_complexivo(
											grupo.id,
											aData.id_tema
										)}
										title="Seleccionar Grupo" 
										class="btn btn-success  btn-xs"
										><i class="fa fa-plus" /> Seleccionar</button
									>
								{:else if !(aData.grupo_seleccionado.grupoTitulacionPostgrado.id == grupo.id)}
									<button
										on:click={() =>
											cambiar_grupo_complexivo(
												grupo.id,
												aData.id_tema,
												aData.grupo_seleccionado.grupoTitulacionPostgrado.id
											)}
										title="Cambiar de Grupo"
										class="btn btn-success btn-xs"
									>
										Cambiar de grupo</button
									>
								{/if}
							{/if}
						{/if}
					</td>
				</tr>
			{:else}
				<tr>No existen grupos disponibles</tr>
			{/each}
		</tbody>
	</table>
</div>
