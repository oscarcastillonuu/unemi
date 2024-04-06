<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let Title = 'Registro de Asistencia';
		let ePersona = {};
		let eInscripcion = {};
		let eMalla = {};
		let eRecordaAademicos = [];
		let eMateriasAsignadas = [];
		let eMatricula = [];
		let cantidad = 0;
		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/asistencia', {});
			console.log(res);
			console.log(errors);
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!res.isSuccess) {
					if (!res.module_access) {
						if (res.redirect) {
							if (res.token) {
								return window.location.href = `${connectionToken}&ret=/${res.redirect}`;
							} else {
								addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
								return {
									status: 302,
									redirect: `/${res.redirect}`
								};
							}
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return {
								status: 302,
								redirect: '/'
							};
						}
					}else{
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					}
				} else {
					console.log(res.data);
					Title = res.data.Title;
					eInscripcion = res.data['eInscripcion'];
					ePersona = eInscripcion.persona;
                    eMalla = res.data['eMalla'];
					eMateriasAsignadas = res.data['materiasasiganadas'];
					cantidad = res.data['cantidad'];
					eMatricula = res.data['eMatricula'];

				}
			}
		}

		return {
			props: {
				Title,
				ePersona,
				eInscripcion,
                eMalla,
				eMateriasAsignadas,
				cantidad,
				eMatricula
			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	// import ComponenteDetalle from './_detalle.svelte';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader, Tooltip } from 'sveltestrap';
	import { variables } from '$lib/utils/constants';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addNotification } from '$lib/store/notificationStore';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import ComponenteCompanero from './_detalleasistencia.svelte';
	import {
		Spinner
	} from 'sveltestrap';
	export let Title;
	export let ePersona;
	export let eInscripcion;
	export let eMalla;
	export let eRecordaAademicos;
	export let eMateriasAsignadas;
	export let cantidad;
	export let eMatricula;
	let load = true;
	let aDataModal = {};
	let modalDetalleContent;
	let modalTitle = '';
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	let mOpenModalGenerico = false;
	let itemsBreadCrumb = [{ text: 'Asistencia', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		if (eMatricula != undefined) {
			load = false;
		}
	});

	const searchAsignature = (e) => {
		//console.log(e);
		
		const tableRowsInterno = document.querySelectorAll('#rwd-table-asignature tbody tr');
		for (let i = 0; i < tableRowsInterno.length; i++) {
			const rowInterno = tableRowsInterno[i];
			const nombre_interno = rowInterno.querySelector('.nombre_asignatura');
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

<svelte:head>
	<title>{Title}</title>
</svelte:head>
<BreadCrumb title={Title} items={itemsBreadCrumb} back={backBreadCrumb} />
{#if !load}

<div class="py-1 py-lg-1">
	<div class="container">
		<div class="row mb-6 align-items-center justify-content-center">
			<div class="col-md-10">
				<div class="row align-items-center ">
					<div class="col-xl-6 col-lg-7 col-md-12 col-12 order-1 text-center text-lg-start ">
						<!-- caption -->
						<span class="text-primary mb-3 d-block text-uppercase fw-semi-bold ls-xl"
							>Mis Asistencias</span
						>
						<h2 class="mb-2 display-4 fw-bold mb-3">{ePersona.nombre_completo}</h2>
						<p class="fs-3 pe-6">{eMalla.display}</p>

						<div class="row">
							<div class="card">
								<table class="table table-bordered table-hover" style="margin-top: 10px">
									<tbody>
									<tr>
										<td style="text-align: center; width: 5%"><i class="bi bi-check-lg" style="color:green;"></i></td>
										<td style="width: 25%">Asistió</td>
										<td style="text-align: center; width: 5%"><i class="bi bi-check-circle-fill" style="color:green"></i></td>
										<td style="width: 65%">Justificó la falta</td>
									</tr>
									<tr>
										<td style="text-align: center; width: 5%"><i class="bi-x-circle-fill" style="color:red"></i></td>
										<td style="width: 25%">Faltó</td>
										<td style="text-align: center; width: 5%"><svg
											xmlns="http://www.w3.org/2000/svg"
											width="24"
											height="24"
											fill="currentColor"
											class="bi bi-file-pdf text-warning"
											viewBox="0 0 16 16"
										>
										<path fill-rule="evenodd" d="M2 8a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11A.5.5 0 0 1 2 8Z"/>
										</svg></td>
										<td style="width: 65%">No consta en lista (No suma ni resta al porcentaje)</td>
									</tr>
									</tbody>
				
								</table>

							</div>
						</div>
					</div>
					<!-- Img -->
					<div class="offset-xl-1 col-xl-5 col-lg-5 col-12 mb-6 mb-lg-0 order-lg-2 text-center ">
						<img
							src={ePersona.foto_perfil}
							onerror="this.onerror=null;this.src='./image.png'"
							alt=""
							class="img-fluid"
						/>
					</div>
				</div>

				
			</div>
		</div>
	</div>
</div>
			
<div class="row">

	<div class="col-lg-12 col-xm-12 col-md-12">
		
		<div class="card">

			<div class="card-body">
				<div class="table-responsive">
					<input
						type="search"
						class="form-control"
						placeholder="Buscar materia"
						style="width: 100% !important;"
						on:keyup={({ target: { value } }) => searchAsignature(value)}
					/>
					<table class="table table-striped table-hover table table-sm mb-0 text-nowrap table table-bordered" id="rwd-table-asignature" >
						<thead class="table-light">
							<tr>
								<th scope="col" class="border-top-0 text-center align-middle " style="width: 20rem;"
									>Materia</th>
                                <th scope="col" class="border-top-0 align-middle " style="width: 5rem;"
									>% Asist.</th>
                                <th scope="col" colspan="{cantidad}" class="border-top-0 text-center align-middle " style="width: 80rem;"
									>Clases</th>
								
							</tr>
						</thead>
						<tbody>
								{#each eMateriasAsignadas as mate}
									<tr>
										<td class="fs-6 align-middle border-top-0 text-wrap nombre_asignatura" style="width: 10rem;">
                                            {mate.materia.nombre_mostrar}
											<br>
											{#if !eMatricula.bloqueomatricula}
											<b>Tiene { mate.porciento_asistencia_justificada_asis }% de asistencia justificada.</b><br>
											<b>Total: </b> <span class="badge bg-info"> {mate.real_dias_asistencia} </span>
											<b>Presentes: </b> <span class="badge bg-success"> {mate.asistencia_real} </span>
											<b>Faltas: </b> <span class="badge bg-danger"> {mate.faltas} </span>

											{/if}
										
										</td>
										<td class="fs-6 align-middle border-top-0 text-center" style="width: 5rem;">
											{#if mate.asistenciafinal < 70}

											<div style="color: red"><strong> {mate.asistenciafinal}%</strong></div>
											{:else}
											<div style="color: green">{mate.asistenciafinal}%</div>

											{/if}
                                            
										
										</td>
										{#if !eMatricula.bloqueomatricula}
											{#if mate.asistencias_lecciones}
											{#if mate.asistencias_lecciones.length > 0  }
												{#each mate.asistencias_lecciones as asist }
													<td class = "fs-6 align-middle border-top-0 text-center">
														{#if asist.valida}

															{#if asist.asistio }

																{#if asist.asistenciajustificada}
																	{asist.fecha_clase_verbose}
																	<br>
																	<a title="{asist.fecha_clase_verbose} ,{asist.leccion.horaentrada }">
																		<i class="bi bi-check-circle-fill" style="color:green"></i>
																	</a>
																{:else}
																	<div class="rotate">{asist.fecha_clase_verbose}</div>
																	
																	<a on:click={() =>
																		toggleModalDetalleAsistencia(
																			asist.id, asist.fecha_clase_verbose
																		)} title="{asist.fecha_clase_verbose} ,{asist.leccion.horaentrada }">
																		<i class="bi bi-check-lg" style="color:green"></i>
																	</a>
																{/if}
															{:else}
																{asist.fecha_clase_verbose}
																<br>
																<a title="{asist.fecha_clase_verbose} ,{asist.leccion.horaentrada }">
																	<i class="bi-x-circle-fill" style="color:red"></i>
																</a>
															{/if}
														{:else}
																{asist.fecha_clase_verbose}
																<br>
																<a title="{asist.fecha_clase_verbose} ,{asist.leccion.horaentrada }">
																	<svg
																xmlns="http://www.w3.org/2000/svg"
																width="24"
																height="24"
																fill="currentColor"
																class="bi bi-file-pdf text-warning"
																viewBox="0 0 16 16"
															>
															<path fill-rule="evenodd" d="M2 8a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11A.5.5 0 0 1 2 8Z"/>
															</svg>
																</a>
														{/if}

													</td>
												{/each}

											{/if}
											{/if}
										{/if}


										
	
											
								{/each}

						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
</div>
{:else}
	<div
		class="m-0 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}

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
