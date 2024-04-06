<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let Title = 'Registro Académico';
		let ePersona = {};
		let eInscripcion = {};
		let eMalla = {};
		let eRecordaAademicos = [];

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const inscripcion = dataSession['inscripcion'];
			const id = inscripcion['id']
			const [res, errors] = await apiGET(fetch, `alumno/notas/${id}/`, {});
			//console.log(res);
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
					Title = res.data.Title;
					eInscripcion = res.data.eInscripcion;
					ePersona = eInscripcion.persona;
					eMalla = res.data.eMalla;
					eRecordaAademicos = res.data.eRecordaAademicos;
				}
			}
		} else {
			return {
				status: 302,
				redirect: '/login'
			};
		}

		return {
			props: {
				Title,
				ePersona,
				eInscripcion,
				eMalla,
				eRecordaAademicos
			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import ComponenteDetalle from './_detalle.svelte';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader, Tooltip } from 'sveltestrap';
	import { variables } from '$lib/utils/constants';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addNotification } from '$lib/store/notificationStore';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	export let Title;
	export let ePersona;
	export let eInscripcion;
	export let eMalla;
	export let eRecordaAademicos;
	let aDataModal = {};
	let modalDetalleContent;
	let modalTitle = '';
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	let mOpenModalGenerico = false;
	let itemsBreadCrumb = [{ text: 'Certificados', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {});

	const toggleModalDetalleMatricula = async (idre, id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, `alumno/record_academico-historico`, {
			action: 'detalle',
			id: id,
			idre: idre
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
				modalDetalleContent = ComponenteDetalle;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Historico de notas';
			}
		}
	};
	const searchAsignature = (e) => {
		//console.log(e);
		
		const tableRowsInterno = document.querySelectorAll('#rwd-table-asignature tbody tr');
		for (let i = 0; i < tableRowsInterno.length; i++) {
			const rowInterno = tableRowsInterno[i];
			const nombre_interno = rowInterno.querySelector('.asignaturas');
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
	function exportTableToExcel(tableID, filename = ''){
		var downloadLink;
		var dataType = 'application/vnd.ms-excel';
		var tableSelect = document.getElementById(tableID);
		var tableHTML = tableSelect.outerHTML.replace(/ /g, '%20');
		
		// Specify file name
		filename = filename?filename+'.xls':'excel_data.xls';
		
		// Create download link element
		downloadLink = document.createElement("a");
		
		document.body.appendChild(downloadLink);
		
		if(navigator.msSaveOrOpenBlob){
			var blob = new Blob(['ufeff', tableHTML], {
				type: dataType
			});
			navigator.msSaveOrOpenBlob( blob, filename);
		}else{
			// Create a link to the file
			downloadLink.href = 'data:' + dataType + ', ' + tableHTML;
		
			// Setting the file name
			downloadLink.download = filename;
			
			//triggering the function
			downloadLink.click();
		}
	}
	let hoveredId = null;

	function handleMouseOver(id) {
	hoveredId = id;
	}

	function handleMouseOut() {
	hoveredId = null;
	}
</script>

<svelte:head>
	<title>{Title}</title>
</svelte:head>
<BreadCrumb title={Title} items={itemsBreadCrumb} back={backBreadCrumb} />
<div class="py-1 py-lg-1">
	<div class="container">
		<div class="row mb-6 align-items-center justify-content-center">
			<div class="col-md-10">
				<div class="row align-items-center ">
					<div class="col-xl-6 col-lg-7 col-md-12 col-12 order-1 text-center text-lg-start ">
						<!-- caption -->
						<span class="text-primary mb-3 d-block text-uppercase fw-semi-bold ls-xl"
							>Mi Record Académico</span
						>
						<h2 class="mb-2 display-4 fw-bold mb-3">{ePersona.nombre_completo}</h2>
						<p class="fs-3 pe-6">{eMalla.display}</p>
						{#if eInscripcion.itinerario}
							<p class="fs-3 pe-6">
								Itinerario:
								<span class="badge bg-primary smaller">ITINERARIO {eInscripcion.itinerario}</span>
							</p>
						{/if}

						<hr class="my-5" />
						<!-- Counter -->
						<div class="row">
							<div class="col-sm mb-3 mb-lg-0">
								<h2 class="h1 fw-bold mb-0 ls-xs">{eInscripcion.total_horas}</h2>
								<p class="mb-0">Total Horas</p>
							</div>
							<div class="col-lg-5 col-sm mb-3 mb-lg-0">
								<h2 class="h1 fw-bold mb-0 ls-xs">{eInscripcion.total_creditos}</h2>
								<p class="mb-0">Total Créditos</p>
							</div>
							<div class="col-sm mb-3 mb-lg-0">
								<h2 class="h1 fw-bold mb-0 ls-xs">{eInscripcion.promedio_general}</h2>
								<p class="mb-0">Promedio General</p>
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
				<div class="row mt-4">
					<div class="col-xl-4 col-lg-6 col-md-6 col-12">
						<!-- Card -->
						<div class="card mb-4">
							<!-- Card body -->
							<div class="card-body">
								<div class="d-flex align-items-center justify-content-between mb-3 lh-1">
									<div>
										<span class="fs-6 text-uppercase fw-semi-bold">Créditos Malla</span>
									</div>
									<div>
										<span class="fe fe-hash fs-3 text-primary" />
									</div>
								</div>
								<h2 class="fw-bold mb-1">{converToDecimal(eInscripcion.total_creditos_malla)}</h2>
							</div>
						</div>
					</div>
					<div class="col-xl-4 col-lg-6 col-md-6 col-12">
						<!-- Card -->
						<div class="card mb-4">
							<!-- Card body -->
							<div class="card-body">
								<div class="d-flex align-items-center justify-content-between mb-3 lh-1">
									<div>
										<span class="fs-6 text-uppercase fw-semi-bold">Créditos Módulos</span>
									</div>
									<div>
										<span class="fe fe-hash fs-3 text-primary" />
									</div>
								</div>
								<h2 class="fw-bold mb-1">{converToDecimal(eInscripcion.total_creditos_modulos)}</h2>
							</div>
						</div>
					</div>
					<div class="col-xl-4 col-lg-6 col-md-6 col-12">
						<!-- Card -->
						<div class="card mb-4">
							<!-- Card body -->
							<div class="card-body">
								<div class="d-flex align-items-center justify-content-between mb-3 lh-1">
									<div>
										<span class="fs-6 text-uppercase fw-semi-bold">Créditos Otros</span>
									</div>
									<div>
										<span class="fe fe-hash fs-3 text-primary" />
									</div>
								</div>
								<h2 class="fw-bold mb-1">{converToDecimal(eInscripcion.total_creditos_otros)}</h2>
							</div>
						</div>
					</div>
					<!--<div class="col-xl-3 col-lg-5 col-md-6 col-12">
						<div class="card mb-4">
							<div class="card-body">
								<div class="d-flex align-items-center justify-content-between mb-3 lh-1">
									<div>
										<span class="fs-6 text-uppercase fw-semi-bold">Aprobadas</span>
									</div>
									<div>
										<span class="fe fe-hash fs-3 text-primary" />
									</div>
								</div>
								<h2 class="fw-bold mb-1">{eInscripcion.total_aprobadas}</h2>
							</div>
						</div>
					</div>
					<div class="col-xl-3 col-lg-5 col-md-6 col-12">
						<div class="card mb-4">
							<div class="card-body">
								<div class="d-flex align-items-center justify-content-between mb-3 lh-1">
									<div>
										<span class="fs-6 text-uppercase fw-semi-bold">Reprobadas</span>
									</div>
									<div>
										<span class="fe fe-hash fs-3 text-primary" />
									</div>
								</div>
								<h2 class="fw-bold mb-1">{eInscripcion.total_reprobadas}</h2>
							</div>
						</div>
					</div>-->
				
					{#if eMalla.horas_practicas}
					<div class="col-xl-6 col-lg-6 col-md-6 col-12">
							<!-- Card -->
							<div class="card mb-4">
								<!-- Card body -->
								<div class="card-body">
									<div class="d-flex align-items-center justify-content-between mb-3 lh-1">
										<div>
											<span class="fs-6 text-uppercase fw-semi-bold">Horas Prácticas</span>
										</div>
										<div>
											<span class="fe fe-hash fs-3 text-primary" />
										</div>
									</div>
									<h2 class="fw-bold mb-1">
										{#if eInscripcion.es_exonerado}
											<span class="badge bd-success"><Icon name="check2" /> Exonerado</span>
										{:else}
											{eInscripcion.total_horas_practicas}/{eMalla.horas_practicas}
										{/if}
									</h2>
								</div>
							</div>
						</div>
					{/if}
					{#if eMalla.horas_vinculacion}
					<div class="col-xl-6 col-lg-6 col-md-6 col-12">
							<!-- Card -->
							<div class="card mb-4">
								<!-- Card body -->
								<div class="card-body">
									<div class="d-flex align-items-center justify-content-between mb-3 lh-1">
										<div>
											<span class="fs-6 text-uppercase fw-semi-bold">Horas Vinculación</span>
										</div>
										<div>
											<span class="fe fe-hash fs-3 text-primary" />
										</div>
									</div>
									<h2 class="fw-bold mb-1">
										{#if eInscripcion.es_exonerado}
											<span class="badge bd-success"><Icon name="check2" /> Exonerado</span>
										{:else}
											{eInscripcion.total_horas_vinculacion}/{eMalla.horas_vinculacion}
										{/if}
									</h2>
								</div>
							</div>
						</div>
					{/if}
				</div>
				
			</div>
		</div>
	</div>
</div>
<div class="row mt-4">
	<div class="col-12">
		<div class="card rounded-3 bg-white">
			<div class="card-body">
				<!--<button on:click|preventDefault={() => exportTableToExcel('rwd-table-asignature')}>Export Table Data To Excel File</button>-->

				<div class="table-responsive">
					<div class="p-0 row">
						<!-- Form -->
						<form class="d-flex align-items-center col-12 col-md-12 col-lg-12">
							<span class="position-absolute ps-3 search-icon">
								<i class="fe fe-search" />
							</span>
							<input
						type="search"
						class="form-control ps-6"
						placeholder="Buscar asignatura"
						style="width: 100% !important;"
						on:keyup={({ target: { value } }) => searchAsignature(value)}
						/>
						</form>
					</div>
					<table class="table table-sm mb-0 text-nowrap table-border table-hover"  id="rwd-table-asignature">
						<thead class="table-light">
							<tr>
								<!--<th scope="col" class="border-0 text-uppercase text-center">#</th>-->
								<th scope="col" class="border-0 text-uppercase text-center" style="width: 12rem;"
									>Asignatura</th
								>
								<th scope="col" class="border-0 text-uppercase text-center">Cred.</th>
								<th scope="col" class="border-0 text-uppercase text-center">Hrs.</th>
								<th scope="col" class="border-0 text-uppercase text-center" style="width: 6rem;"
									>Profesor/Observaciones</th
								>
								<th scope="col" class="border-0 text-uppercase text-center">Nota</th>
								<th scope="col" class="border-0 text-uppercase text-center">Asist.(%)</th>
								<th scope="col" class="border-0 text-uppercase text-center">Fecha</th>
								<th scope="col" class="border-0 text-uppercase text-center">Hom.</th>
								<th scope="col" class="border-0 text-uppercase text-center">Cred.</th>
								<th scope="col" class="border-0 text-uppercase text-center">Prom.</th>
								<th scope="col" class="border-0 text-uppercase text-center">Estado</th>
							</tr>
						</thead>
						<tbody>
							{#if eRecordaAademicos.length > 0}
								{#each eRecordaAademicos as eRecordaAademico, i}
									<tr class="text-dark">
										<!--<td class="text-center align-middle border-top-0">{i + 1}</td>-->
										<td class="fs-6 align-middle border-top-0 text-wrap asignaturas" style="width: 12rem;">
											{eRecordaAademico.asignatura.nombre}
											{#if eRecordaAademico.asignaturamalla || eRecordaAademico.matriculas > 1}
												<br />
												{#if eRecordaAademico.asignaturamalla}
													<span class="badge bg-primary"
														>{eRecordaAademico.asignaturamalla.nivelmalla.nombre}</span
													>
													
													{#if eRecordaAademico.asignaturamalla.itinerario}
														<span class="badge bg-secondary"
															>ITINERARIO {eRecordaAademico.asignaturamalla.itinerario}</span
														>
													{/if}
												{:else}
													<span class="badge bg-dark">NO CONSTA EN MALLA</span>
												{/if}
												{#if eRecordaAademico.matriculas > 1}
												<button
												type="button" on:click={() => toggleModalDetalleMatricula(eRecordaAademico.id, eInscripcion.id)}
												class="btn btn-danger btn-sm p-0">{eRecordaAademico.matriculas} MAT.</button>
												{/if}
											{/if}
											{#if eRecordaAademico.ofimatica }
											<a
												href="{eRecordaAademico.ofimatica.archivocertificado}"
												title="Descargar certificado"
												target="_blank"
												>
												<img 
												width="30"
												height="30"
												src={hoveredId === eRecordaAademico.id ? "/assets/images/svg/pdf_download_on.svg" : "/assets/images/svg/pdf_download_off.svg"}
												on:mouseover={() => handleMouseOver(eRecordaAademico.id)}
												on:mouseout={handleMouseOut}
												/>
											</a>
											{/if}
										</td>
										<td class="text-center align-middle border-top-0"
											>{eRecordaAademico.asignaturamalla
												? eRecordaAademico.asignaturamalla.creditos
												: eRecordaAademico.creditos}</td
										>
										<td class="text-center align-middle border-top-0"
											>{eRecordaAademico.asignaturamalla
												? eRecordaAademico.asignaturamalla.horas
												: eRecordaAademico.horas}</td
										>
										<td class="text-left align-middle border-top-0 text-wrap" style="width: 6rem;">
											{#if eRecordaAademico.profesor}
												<p class="text-break font-monospace mt-0 mb-0">
													{eRecordaAademico.profesor.persona.nombre_completo}
												</p>
											{/if}
											{#if eRecordaAademico.observaciones}
												<p class="text-break font-monospace mt-0 mb-0">
													{eRecordaAademico.observaciones}
												</p>
											{/if}
										</td>
										<td class="text-center align-middle border-top-0">
											{#if eRecordaAademico.tiene_deuda_matricula}
												<span
													class="badge bg-warning text-dark"
													id={`tooltip-deuda-nota-${eRecordaAademico.id}`}
													><Icon name="info" /></span
												>
												<Tooltip
													target={`tooltip-deuda-nota-${eRecordaAademico.id}`}
													placement="top"
													>Estimado/a aspirante, aun le quedan VALORES PENDIENTES POR PAGAR</Tooltip
												>
											{:else if !eRecordaAademico.ocultarnota}
												{eRecordaAademico.nota}
											{/if}
										</td>
										<td class="text-center align-middle border-top-0">
											{#if eRecordaAademico.tiene_deuda_matricula}
												<span
													class="badge bg-warning text-dark"
													id={`tooltip-deuda-asistencia-${eRecordaAademico.id}`}
													><Icon name="info" /></span
												>
												<Tooltip
													target={`tooltip-deuda-asistencia-${eRecordaAademico.id}`}
													placement="top"
													>Estimado/a aspirante, aun le quedan VALORES PENDIENTES POR PAGAR</Tooltip
												>
											{:else if !eRecordaAademico.ocultarnota}
												{eRecordaAademico.asistencia}%
											{/if}
										</td>
										<td class="text-center align-middle border-top-0">
											{eRecordaAademico.fecha}
										</td>
										<td class="text-center" style="vertical-align: middle;">
											{#if eRecordaAademico.homologada || eRecordaAademico.convalidacion}
												<Icon name="check2" />
												{#if eRecordaAademico.archivohomologacion}
													<br />
													<a
														href={eRecordaAademico.archivohomologacion}
														target="_blank"
														class="fe fe-download"
														download=""
													/>
												{:else if eRecordaAademico.archivoconvalidacion}
													<br />
													<a
														href={eRecordaAademico.archivoconvalidacion}
														target="_blank"
														class="fe fe-download"
														download=""
													/>
												{/if}
											{/if}
										</td>
										<td class="text-center align-middle border-top-0">
											{#if eRecordaAademico.valida}
												<Icon name="check2" />
											{/if}
										</td>
										<td class="text-center align-middle border-top-0">
											{#if eRecordaAademico.validapromedio}
												<Icon name="check2" />
											{/if}
										</td>
										<td class="text-center align-middle border-top-0">
											{#if eRecordaAademico.noaplica}
												<span class="badge bg-warning text-dark">NO APLICA</span>
											{:else if eRecordaAademico.aprobada}
												<span class="badge bg-success">APROBADA</span>
											{:else}
												<span class="badge bg-danger">REPROBADA</span>
											{/if}
										</td>
									</tr>
								{/each}
							{/if}
						</tbody>
						<tfoot />
					</table>
				</div>
			</div>
		</div>
	</div>
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
