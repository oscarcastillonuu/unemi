<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let eArchivoDescarga = [];


		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/archivo_descarga', {});
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
					// console.log(res.data);
					eArchivoDescarga = res.data['eArchivoDescarga'];

				}
			}
		}

		return {
			props: {
				eArchivoDescarga,

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
	export let eArchivoDescarga;

	let mOpenModalGenerico = false;
	let mOpenConfirmarImportarNotasIngles = false;
	let modalTitle = '';
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
		(mOpenConfirmarImportarNotasIngles = !mOpenConfirmarImportarNotasIngles);

	let itemsBreadCrumb = [{ text: 'Enlaces de programas', active: true, href: undefined }];
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

	const searchCongreso = (e) => {
		//console.log(e);
		
		const tableRowsInterno = document.querySelectorAll('#rwd-table-congreso tbody tr');
		for (let i = 0; i < tableRowsInterno.length; i++) {
			const rowInterno = tableRowsInterno[i];
			const nombre_interno = rowInterno.querySelector('.nombre_congreso');
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
			loadAjax({}, 'alumno/archivo_descarga', 'GET')
				.then((response) => {
					if (response.value.isSuccess) {
						eArchivoDescarga = response.value.data['eArchivoDescarga'];


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



</script>

<svelte:head>

	<title>Enlaces de programas</title>
</svelte:head>
<BreadCrumb title="Enlaces de programas" items={itemsBreadCrumb} back={backBreadCrumb} />

<div class="row">

	<div class="col-lg-12 col-xm-12 col-md-12">
		
		<div class="card">

			<div class="card-body">
                <div class="alert alert-info d-flex align-items-center text-justify" role="alert">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="24"
                        height="24"
                        fill="currentColor"
                        class="bi bi-info-circle-fill me-2"
                        viewBox="0 0 16 16"
                    >
                        <path
                            d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"
                        />
                    </svg>
                    <div>
                        Solo podrán acceder a la descarga del archivo si posee su cuenta de correo institucional vinculada con google.
                    </div>
                </div>
				<div class="table-responsive">
					<input
						class="form-control"
						placeholder="Buscar programa"
						style="width: 100% !important;"
                        on:keyup={({ target: { value } }) => searchCongreso(value)}

					/>
					<table class="table mb-0 table-hover" id="rwd-table-congreso" >
						<thead class="table-light">
							<tr>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Programa</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Nombre del programa</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Version</th>
                                <th scope="col" class="border-top-0 text-center align-middle " style="width: 22rem;"
									>Enlace de descarga</th>

							</tr>
						</thead>
						<tbody>
							{#if eArchivoDescarga.length > 0}
								{#each eArchivoDescarga as pro}
									<tr>
										<td class="fs-6 align-middle border-top-0 text-center ">
                                            {#if pro.imagen }
                                            <img src="https://sga.unemi.edu.ec{ pro.imagen }" alt="" style="width: 50px">
                                             {/if}										
                                        </td>
										<td class="fs-6 align-middle border-top-0 text-center nombre_congreso">
                                        {pro.nombreprograma}
                                        </td>
										<td class="fs-6 align-middle border-top-0 text-center">
                                  
										{pro.version}
                                        </td>
										<td class="fs-6 align-middle border-top-0 text-center">
						
												<a href="{pro.enlacedescarga}" target="_blank">
											<svg
												xmlns="http://www.w3.org/2000/svg"
												width="24"
												height="24"
												fill="currentColor"
												class="bi bi-file-pdf text-success"
												viewBox="0 0 16 16"
											>

												<path fill-rule="evenodd" d="M3.5 10a.5.5 0 0 1-.5-.5v-8a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 .5.5v8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 0 0 1h2A1.5 1.5 0 0 0 14 9.5v-8A1.5 1.5 0 0 0 12.5 0h-9A1.5 1.5 0 0 0 2 1.5v8A1.5 1.5 0 0 0 3.5 11h2a.5.5 0 0 0 0-1h-2z"/>
												<path fill-rule="evenodd" d="M7.646 15.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 14.293V5.5a.5.5 0 0 0-1 0v8.793l-2.146-2.147a.5.5 0 0 0-.708.708l3 3z"/>
											
											</svg>
												</a>
											
										</td>
									
								{/each}
							{:else}
								<tr>
									<td colspan="8" class="text-center">NO EXISTEN APLICACIONES</td>
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



