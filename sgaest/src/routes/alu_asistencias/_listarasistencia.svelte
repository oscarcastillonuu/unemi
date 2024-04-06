<script lang="ts">
	import { onMount } from 'svelte';
    import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import { loading } from '$lib/store/loadingStore';
	import { addNotification } from '$lib/store/notificationStore';
    import ComponenteCompanero from './_detalleasistencia.svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';

    let aDataModal = {};
	let modalDetalleContent;
	let modalTitle = '';
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	let mOpenModalGenerico = false;

	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	export let aData;
	let asistencia = [];
	let nombres = '';
	onMount(async () => {
		asistencia = aData.asistencias;
		nombres = aData.nombre;
	});
    const toggleModalDetalleAsistencia= async (id, fecha) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		console.log("ENTRA")
		const [res, errors] = await apiPOST(fetch, 'alumno/asistencia', {
			
			action: 'detalleAsistencia',
			id: id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				//console.log(res.data);
				aDataModal = res.data;
				modalDetalleContent = ComponenteCompanero;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = `Asistencia del ${fecha}`;
			}
		}
	};
</script>
<div class="row">
	<!-- <div class="card"> -->
		<table class="table table-bordered table-hover" style="margin-top: 10px">
			<tbody>
				<tr>
					<td style="text-align: center; "
						><i class="bi bi-check-lg" style="color:green;" /></td
					>
					<td style="width: 5%">Asistió</td>
					<td style="text-align: center;"
						><i class="bi bi-check-circle-fill" style="color:green" /></td
					>
					<td style="">Justificó la falta</td>
				<!-- </tr>
				<tr> -->
					<td style="text-align: center;"
						><i class="bi-x-circle-fill" style="color:red" /></td
					>
					<td style="">Faltó</td>
					<td style="text-align: center; "
						><svg
							xmlns="http://www.w3.org/2000/svg"
							width="24"
							height="24"
							fill="currentColor"
							class="bi bi-file-pdf text-warning"
							viewBox="0 0 16 16"
						>
							<path
								fill-rule="evenodd"
								d="M2 8a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11A.5.5 0 0 1 2 8Z"
							/>
						</svg></td
					>
					<td style=""
						>No consta en lista (No suma ni resta al porcentaje)</td
					>
				</tr>
			</tbody>
		</table>
	<!-- </div> -->
</div>
<div class="text-center">
	<br />
	<b>{nombres}</b>
	<br />
	<br />
</div>
<div class="table-responsive">
	<table
		class="table  table table-sm mb-0 text-nowrap table table-bordered"
		id="rwd-table-asignature"
	>
		<thead class="table-light">
			<tr>
				<th
				
					class="border-top-0 text-center align-middle "
					style="width: 80rem;">Fecha</th
				>
			
				<th
				
					class="border-top-0 text-center align-middle "
					style="width: 80rem;">Hora</th
				>
				<th
				
					class="border-top-0 text-center align-middle "
					style="width: 80rem;">Estado</th
				>
				
			</tr>
		</thead>
		<tbody
			>
				{#if asistencia}
					{#if asistencia.length > 0}
						{#each asistencia as asist}
						<tr>
							<td class="fs-6 align-middle border-top-0 text-center">

								{asist.fecha_clase_verbose}

							</td>
							
							<td class="fs-6 align-middle border-top-0 text-center">
								{asist.leccion.horaentrada}
							</td>

							<td class="fs-6 align-middle border-top-0 text-center">

								{#if asist.valida}
									{#if asist.asistio}
										{#if asist.asistenciajustificada}
											<a title="{asist.fecha_clase_verbose} ,{asist.leccion.horaentrada}">
												<i class="bi bi-check-circle-fill" style="color:green" />
											</a>
										{:else}
											<!-- <i class="bi bi-check-lg" style="color:green" /> -->
											<a on:click={() =>
																		toggleModalDetalleAsistencia(
																			asist.id, asist.fecha_clase_verbose
																		)} title="{asist.fecha_clase_verbose} ,{asist.leccion.horaentrada }">
																		<i class="bi bi-check-lg" style="color:green"></i>
																	</a>
										{/if}
									{:else}
										<a title="{asist.fecha_clase_verbose} ,{asist.leccion.horaentrada}">
                                            <a on:click={() =>
                                                toggleModalDetalleAsistencia(
                                                    asist.id, asist.fecha_clase_verbose
                                                )} title="{asist.fecha_clase_verbose} ,{asist.leccion.horaentrada }">
                                                <i class="bi-x-circle-fill" style="color:red" />
                                            </a>
										</a>
									{/if}
								{:else}
									<a title="{asist.fecha_clase_verbose} ,{asist.leccion.horaentrada}">
										<svg
											xmlns="http://www.w3.org/2000/svg"
											width="24"
											height="24"
											fill="currentColor"
											class="bi bi-file-pdf text-warning"
											viewBox="0 0 16 16"
										>
											<path
												fill-rule="evenodd"
												d="M2 8a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11A.5.5 0 0 1 2 8Z"
											/>
										</svg>
									</a>
								{/if}
							</td>
						</tr>
						{/each}
					{:else}
						<td colspan="3"  class="fs-6 align-middle border-top-0 text-center">
							NO TIENE ASISTENCIAS EN ESTE MES
						</td>
					{/if}
				{:else}
					<td colspan="3" class="fs-6 align-middle border-top-0 text-center">
						NO TIENE ASISTENCIAS EN ESTE MES
					</td>
				{/if}
			
		</tbody>
	</table>
</div>
{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size="xl"
	/>
{/if}
