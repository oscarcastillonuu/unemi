<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eMisCitas = [];


		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/miscitas', {});
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					if (!res.module_access) {
						return {
							status: 302,
							redirect: '/'
						};
					}
				} else {
					//console.log(res.data);
					eMisCitas = res.data['eMisCitas'];

				}
			}
		}

		return {
			props: {
				eMisCitas,

			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { onMount } from 'svelte';
	import { variables } from '$lib/utils/constants';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader, Tooltip } from 'sveltestrap';
import Error from '../__error.svelte';
	export let eMisCitas;

	let mOpenModalGenerico = false;
	let mOpenConfirmarImportarNotasIngles = false;
	let modalTitle = '';
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
		(mOpenConfirmarImportarNotasIngles = !mOpenConfirmarImportarNotasIngles);

	let itemsBreadCrumb = [{ text: 'Mis Citas Medicas', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {});

	const loadAjax = async (data, url, method = undefined) =>
		new Promise(async (resolve, reject) => {
			if (method === undefined) {
				const [res, errors] = await apiPOST(fetch, url, data);
				//console.log(errorsCertificates);
				if (errors.length > 0) {
					reject({
						error: true,
						message: errors[0].error
					});
				} else {
					resolve({
						error: false,
						value: res
					});
				}
			} else {
				const [res, errors] = await apiGET(fetch, url, data);
				//console.log(errorsCertificates);
				if (errors.length > 0) {
					reject({
						error: true,
						message: errors[0].error
					});
				} else {
					resolve({
						error: false,
						value: res
					});
				}
			}
		});

	const searchCitas = (e) => {
		//console.log(e);
		
		const tableRowsInterno = document.querySelectorAll('#rwd-table-citas tbody tr');
		for (let i = 0; i < tableRowsInterno.length; i++) {
			const rowInterno = tableRowsInterno[i];
			const nombre_interno = rowInterno.querySelector('.citas_indicaciones');
			if (
				converToAscii(nombre_interno.innerText.toLowerCase()).indexOf(
					converToAscii(e.toLowerCase())
				) === -1
			) {
				rowInterno.style.display = 'none';
			} else {
				rowInterno.style.display = '';
			}
		}
		
		
	};

	const loadInitial = () =>
		new Promise((resolve, reject) => {
			loadAjax({}, 'alumno/miscitas', 'GET')
				.then((response) => {
					if (response.value.isSuccess) {
						eMisCitas = response.value.data['eMisCitas'];


						resolve({
							error: false,
							value: true
						});
					} else {
						reject({
							error: true,
							message: response.value.message
						});
					}
				})
				.catch((error) => {
					reject({
						error: true,
						message: error.message
					});
				});
		});





	// $: {
	// 	//console.log(id_periodo);
	// 	//console.log(id_inscripcion);
	// }
</script>

<svelte:head>
	<title>Mis Citas Medicas</title>
</svelte:head>
<BreadCrumb title="Mis Citas Medicas" items={itemsBreadCrumb} back={backBreadCrumb} />

<div class="row">

	<div class="col-lg-12 col-xm-12 col-md-12">
		
		<div class="card">

			<div class="card-body">
				<div class="table-responsive">
					<input
						type="search"
						class="form-control"
						placeholder="Buscar citas medicas"
						style="width: 100% !important;"
						on:keyup={({ target: { value } }) => searchCitas(value)}
					/>
					<table class="table table-striped table-hover table table-sm mb-0 text-nowrap table-border table-hover" id="rwd-table-citas" >
						<thead class="table-light">
							<tr>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Fecha/Hora</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Medico</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Indicaciones</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Tipo</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Estado</th>
								
							</tr>
						</thead>
						<tbody>
							{#if eMisCitas.length > 0}
								{#each eMisCitas as eCitas}
									<tr>
										<td class="fs-6 align-middle border-top-0 text-center">
                                            {eCitas.fecha}
										
										</td>
										<td class="fs-6 align-middle border-top-0 text-center">
                                            {eCitas.medico.nombre_completo}
										
										</td>
										<td class="fs-6 align-middle border-top-0 text-center citas_indicaciones">
                                            {#if eCitas.indicaciones}
                                            {eCitas.indicaciones}
                                            {/if}
										
										</td>
										<td class="fs-6 align-middle border-top-0 text-center">
                                            {#if eCitas.tipoconsulta == 1}
                                                <span class="badge bg-success"> MÉDICA </span>
                                            {:else if eMisCitas.tipoconsulta == 2}
                                            <span class="badge bg-success"> PSICOLÓGICA </span>
                                            {:else}
                                            <span class="badge bg-success"> ODONTOLÓGICA </span>
                                            {/if}

										</td>
										<td class="fs-6 align-middle border-top-0 text-center">

                                            {#if eCitas.vigente && !eCitas.asistio}
                                                <span class="badge bg-warning"> PENDIENTE </span>
                                            {:else}
                                                {#if eCitas.asistio}
                                                <span class="badge bg-success"> ASISTIO </span>
                                                {:else}
                                                <span class="badge bg-danger"> NO ASISTIO </span>

                                                {/if}
                                            {/if}

										</td>
										
										
	
											
								{/each}
							{:else}
								<tr>
									<td colspan="8" class="text-center">NO EXISTEN CITAS REGISTRADAS</td>
								</tr>
							{/if}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
</div>


<style>
	/* 	CSS variables can be used to control theming.
			https://github.com/rob-balfre/svelte-select/blob/master/docs/theming_variables.md
	*/

	form {
		/*max-width: 400px;*/
		background: #f4f4f4;
		padding: 0;
		border-radius: 4px;
	}

	label {
		margin: 0 0 10px;
	}
	.themed {
		--border: 3px solid blue;
		--borderRadius: 10px;
		--placeholderColor: blue;
	}
</style>
