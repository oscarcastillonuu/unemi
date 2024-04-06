<script lang="ts">
	export let aData;
	import { browserGet, apiPOST, apiPOSTFormData, apiGET } from '$lib/utils/requestUtils';
	import Swal from 'sweetalert2';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { onMount } from 'svelte';

	const dispatch = createEventDispatcher();

	const actionInscribirme = async (id,grupo_nombre,fecha,horario) => {
		const mensaje = {
			title: 'CONFIRMACIÓN DE INSCRIPCIÓN',
			html: '¿ESTÁ SEGURO DE INSCRIBIRSE EN EL GRUPO: <b>'+grupo_nombre+ '</b> CON FECHA: '+ '<b>'+ fecha+ '</b> '+ 'CON HORARIO: '+ ' <b>'+horario+ '</b>?',
			type: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: `Confirmar`,
			cancelButtonText: 'Cancelar'
		};
		Swal.fire(mensaje)
		.then(async (result)=>{
			if (result.value) {
				loading.setLoading(true, 'Cargando, espere por favor...');
				const [res, errors] = await apiPOST(fetch, 'alumno/idiomas	', {
					action: 'guardar_inscripcion',
					id:id,
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				if (errors.length > 0) {
					addToast({ type: 'warning', header: 'Advertencia', body: errors[0].error });
					return;
				} else {
					if (!res.isSuccess) {
						addToast({ type: 'warning', header: 'Advertencia', body: res.message });
						return;
					} else {
						dispatch('actionRun', { action: 'nextProccess', value: 1});//closeModalReload
					}
				}
			}
		}).catch((error) => {
			addToast({ type: 'warning', header: 'Advertencia', body: error });
			return;
		});
	}

	onMount(async () => {});
	let grupo = aData.eGrupo;
</script>

<div class="row">
	<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
		<thead class="table-ligth">
			<tr>
				<th scope="col" class="border-top-0 text-center align-middle ">N°</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Grupo</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Cupos disponibles</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Fecha</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Día</th>
				<th scope="col" class="border-top-0 text-center align-middle ">Horarios</th>
				<th scope="col" class="border-top-0 text-center align-middle " />
			</tr>
		</thead>
		<tbody>
		{#if grupo}
			{#if grupo.existe_cupo_disponible === true}
				<tr>
					<td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
						{grupo.orden }
					</td>
					<td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
						{grupo.nombre}
					</td>
					<td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
						{grupo.cupos_disponible}
					</td>

					<td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
						{grupo.fecinicio}
					</td>

					<td scope="col" class="fs-6 align-middle text-center border-top-0 text-justify text-wrap">
						{grupo.inicio_display}
					</td>

					<td scope="col" class="fs-6 align-middle text-center border-top-0 text-center text-wrap">
							{grupo.horario}
					</td>
					<td scope="col" class="fs-6 align-middle text-center border-top-0 text-center text-wrap">
						{#if grupo.existe_cupo_disponible == true}
							<button on:click|preventDefault={() => actionInscribirme(grupo.id,grupo.nombre,grupo.fecha_inicio_display,grupo.horario)} class="btn btn-info rounded-pill text-white" type="button">Inscribirme</button>
						{:else}
							<span class="">No existen cupos disponibles</span>
						{/if}


					</td>

				</tr>
			{:else}
				<tr><td colspan="7">No existen grupos disponibles</td></tr>
			{/if}
		{:else}
			<tr><td>No existen grupos disponibles</td></tr>
		{/if}


		</tbody>
	</table>
</div>
