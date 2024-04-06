<script context="module" lang="ts">
	import { browserGet, apiPOST } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	export const load: Load = async ({ fetch }) => {
		let items_periodos = [];
		let items_matriculas = [];
		let eCertificadosInternos = [];
		let eCertificadosExternos = [];
		let eMatriculas = [];
		let item_matricula,
			periodo,
			inscripcion = {};

		const ds = browserGet('dataSession');
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			periodo = dataSession['periodo'];
			inscripcion = dataSession['inscripcion'];

			const eperiodos = dataSession['periodos'];
			//items_periodos.push({ value: '0', label: '--NINGUNO--' });
			for (const i in eperiodos) {
				items_periodos.push({ value: eperiodos[i]['id'], label: eperiodos[i]['nombre_completo'] });
			}

			const [resCertificates, errorsCertificates] = await apiPOST(
				fetch,
				'alumno/certificado/all',
				{}
			);
			//console.log(errorsCertificates);
			if (errorsCertificates.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errorsCertificates[0].error });
				return {
					status: 302,
					redirect: '/'
				};
			} else {
				if (!resCertificates.isSuccess) {
					if (!resCertificates.module_access) {
						if (resCertificates.redirect) {
							if (resCertificates.token) {
								return (window.location.href = `${connectionToken}&ret=/${resCertificates.redirect}`);
							} else {
								addToast({
									type: 'error',
									header: 'Ocurrio un error',
									body: resCertificates.message
								});
								return {
									status: 302,
									redirect: `/${resCertificates.redirect}`
								};
							}
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return {
								status: 302,
								redirect: '/'
							};
						}
					} else {
						addToast({ type: 'error', header: 'Ocurrio un error', body: resCertificates.message });
					}
				} else {
					//console.log(resCertificates.data);
					eCertificadosInternos = resCertificates.data['internos'];
					eCertificadosExternos = resCertificates.data['externos'];
					eMatriculas = resCertificates.data['matriculas'];
					for (const i in eMatriculas) {
						if (eMatriculas[i]['nivel']['periodo']['id'] === periodo['id']) {
							item_matricula = {
								value: eMatriculas[i]['id'],
								label: eMatriculas[i]['nivel']['periodo']['nombre']
							};
						}
						items_matriculas.push({
							value: eMatriculas[i]['id'],
							label: eMatriculas[i]['nivel']['periodo']['nombre']
						});
					}
				}
			}
		}

		return {
			props: {
				items_periodos,
				items_matriculas,
				item_matricula,
				inscripcion,
				eCertificadosInternos,
				eCertificadosExternos,
				eMatriculas
			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { scale } from 'svelte/transition';
	import Typeahead from 'svelte-typeahead'; //https://metonym.github.io/svelte-typeahead/
	import Select from 'svelte-select/Select.svelte'; //https://github.com/rob-balfre/svelte-select
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	export let item_matricula;
	export let items_periodos;
	export let items_matriculas;
	export let inscripcion;
	export let eCertificadosInternos;
	export let eCertificadosExternos;
	export let eMatriculas;
	let id_matricula = 0;
	let id_inscripcion = 0;
	let open = false;
	let title_modal = 'Certificado';
	let certificado_url = undefined;
	let itemsBreadCrumb = [{ text: 'Certificados', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };

	const toggle = () => (open = !open);

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		id_matricula = item_matricula ? item_matricula.value : 0;
		id_inscripcion = inscripcion['id'];
	});

	function handleSelect(event) {
		//console.log(event.detail);
		id_matricula = event.detail.value;
	}

	function handleClear(e) {
		//favouriteFood = undefined;
		//console.log(e);
		id_matricula = 0;
	}
	const searchCertificados = (e, type) => {
		//console.log(e);

		if (type === 'interno') {
			//console.log('interno');
			const tableRowsInterno = document.querySelectorAll('#rwd-table-interno tbody tr');
			//console.log('tableRowsInterno', tableRowsInterno);
			for (let i = 0; i < tableRowsInterno.length; i++) {
				const rowInterno = tableRowsInterno[i];
				const nombre_interno = rowInterno.querySelector('.certificado_name');
				//console.log('nombre_interno: ', nombre_interno.innerText);
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
		} else {
			//console.log('externo');
			const tableRowsExterno = document.querySelectorAll('#rwd-table-externo tbody tr');
			for (let i = 0; i < tableRowsExterno.length; i++) {
				const rowExterno = tableRowsExterno[i];
				const nombre_externo = rowExterno.querySelector('.certificado_name');
				//console.log('nombre_externo: ', nombre_externo.innerText);
				if (
					converToAscii(nombre_externo.innerText.toLowerCase()).indexOf(
						converToAscii(e.toLowerCase())
					) === -1
				) {
					rowExterno.style.display = 'none';
				} else {
					rowExterno.style.display = '';
				}
			}
		}
	};

	const action_to_download = async (eCertificado: object): Promise<void> => {
		let parms = {};
		let res = undefined;
		loading.setLoading(true, 'Cargando, espere por favor...');
		if (eCertificado.tipo_certificacion === 1) {
			/*nhref = `/reportes?action=run&n=${eCertificado.reporte.nombre}&${
				eCertificado.reporte.version === 2 ? 'vqr' : 'variableqr'
			}=${id_matricula}`;*/
			parms['n'] = eCertificado.reporte.nombre;
			if (eCertificado.reporte.version === 2) parms['vqr'] = id_matricula;
			else parms['variableqr'] = id_matricula;

			res = await action_print_ireport(eCertificado.reporte.tipos, parms);
		} else if (eCertificado.tipo_certificacion === 2) {
			/*nhref = `/reportes?action=run&n=${eCertificado.reporte.nombre}&${
				eCertificado.reporte.version === 2 ? 'vqr' : 'variableqr'
			}=${id_inscripcion}`;*/
			parms['n'] = eCertificado.reporte.nombre;
			if (eCertificado.reporte.version === 2) parms['vqr'] = id_inscripcion;
			else parms['variableqr'] = id_inscripcion;

			res = await action_print_ireport(eCertificado.reporte.tipos, parms);
		} else if (eCertificado.tipo_certificacion === 3) {
			//let valMatricula = {};
			let id_tipo_periodo = 0;
			let is_cerrada = false;
			for (let i in eMatriculas) {
				//console.log(i); // key
				//console.log(eMatriculas[i]); // value against the key
				if (eMatriculas[i]['id'] === id_matricula) {
					id_tipo_periodo = eMatriculas[i]['nivel']['periodo']['tipo']['orden_id'];
					is_cerrada = eMatriculas[i]['cerrada'];
				}
			}

			if (id_tipo_periodo === 2) {
				if (!is_cerrada) {
					const mensaggeWarning = {
						toast: true,
						position: 'top-center',
						type: 'warning',
						icon: 'warning',
						title: 'Certificado no puede ser generado, periodo académico en curso.',
						showConfirmButton: true,
						timer: 6000
					};
					Swal.fire(mensaggeWarning);
					return;
				}
			}
			
			/*nhref = `/reportes?action=run&n=${eCertificado.reporte.nombre}&${
				eCertificado.reporte.version === 2 ? 'vqr' : 'variableqr'
			}=${id_matricula}`;*/
			parms['n'] = eCertificado.reporte.nombre;
			if (eCertificado.reporte.version === 2) parms['vqr'] = id_matricula;
			else parms['variableqr'] = id_matricula;

			res = await action_print_ireport(eCertificado.reporte.tipos, parms);
		}
		//console.log(eCertificado.tipo_certificacion);
		//console.log(nhref);
		if (res !== undefined) {
			//open = true;
			//title_modal = `[${eCertificado.codigo}] ${eCertificado.certificacion}`;
			//certificado_url = res.data.reportfile;
			//console.log(certificado_url);
			if (res.data.es_background) {
				const noti = {
					//toast: true,
					position: 'top-center',
					type: 'info',
					icon: 'info',
					title: res.message,
					showConfirmButton: true
					//timer: 6000
				};
				Swal.fire(noti);
			} else {
				window.open(`${res.data.reportfile}`, '_blank');
			}
		}
		loading.setLoading(false, 'Cargando, espere por favor...');

		return;
	};

	$: {
		//console.log(id_periodo);
		//console.log(id_inscripcion);
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
	<title>Certificados</title>
</svelte:head>
<BreadCrumb title="Certificados" items={itemsBreadCrumb} back={backBreadCrumb} />

<div class="row">
	<div class="col-lg-12 col-md-12 col-12 mb-2">
		{#if items_periodos.length > 0}
			<form>
				<Select
					id="select_periodo"
					items={items_matriculas}
					value={item_matricula}
					on:select={handleSelect}
					on:clear={handleClear}
					isClearable={false}
					placeholder="Seleccione un periodo académico"
				/>
			</form>
		{/if}
	</div>
</div>

<div class="row">
	<div class="col-lg-6 col-xm-12 col-md-12">
		<div class="card">
			<div class="card-header text-center">
				<h4 class="mb-0 display-6">CERTIFICADOS INTERNOS</h4>
			</div>
			<div class="card-header">
				<div class="alert alert-info d-flex align-items-center" role="alert">
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
						Los certificados internos son aquellas certificaciones que se emiten para tramites en la
						misma UNEMI tales como cambio de carrera o para el proceso de titulación.
					</div>
				</div>
			</div>

			<div class="card-body">
				<div class="table-responsive">
					<input
						type="search"
						class="form-control"
						placeholder="Buscar certificado"
						style="width: 100% !important;"
						on:keyup={({ target: { value } }) => searchCertificados(value, 'interno')}
					/>
					<table class="table mb-0 table-hover" style="width: 100%;" id="rwd-table-interno">
						<thead class="table-light">
							<tr>
								<th scope="col" class="border-top-0 text-center">Certificado</th>
								<th scope="col" class="border-top-0 text-center">Código</th>
								<th scope="col" class="border-top-0 text-center">Versión</th>
								<th scope="col" class="border-top-0 text-center">Descargar</th>
							</tr>
						</thead>
						<tbody>
							{#if eCertificadosInternos.length > 0}
								{#each eCertificadosInternos as eCertificado}
									<tr>
										
										<td class="align-middle certificado_name">
											{eCertificado.certificacion}<br />
											(Tiempo de vigencia de
											{#if eCertificado.tipo_vigencia === 0}
												<span class="badge bg-badge">NINGUNA</span>
											{:else if eCertificado.tipo_vigencia == 1}
												<span class="badge bg-danger">{eCertificado.vigencia} HORAS</span>
											{:else if eCertificado.tipo_vigencia == 2}
												<span class="badge bg-warning text-dark">{eCertificado.vigencia} DÍAS</span>
											{:else if eCertificado.tipo_vigencia == 3}
												<span class="badge bg-success">{eCertificado.vigencia} MESES</span>
											{:else}
												{#if eCertificado.vigencia > 1}
													<span class="badge bg-info text-dark">{eCertificado.vigencia} AÑOS</span>
												{:else}
													<span class="badge bg-info text-dark">{eCertificado.vigencia} AÑO</span>
												{/if}
											{/if})
										</td>
										<td class="align-middle text-center"
											>{eCertificado.codigo}<br />{eCertificado.reporte.codigo}</td
										>
										<td class="align-middle text-center">{eCertificado.version}</td>
										<td class="align-middle text-center">
											<div class="icon-shape icon-lg rounded-3">
												<a
													href="#{eCertificado.id}"
													on:click|preventDefault={() => action_to_download(eCertificado)}
												>
													<img 
													width="50"
													height="50"
													src={hoveredId === eCertificado.id ? "/assets/images/svg/pdf_download_on.svg" : "/assets/images/svg/pdf_download_off.svg"}
													on:mouseover={() => handleMouseOver(eCertificado.id)}
													on:mouseout={handleMouseOut}
													/>
												</a>
											</div>
										</td>

									</tr>
								{/each}
							{:else}
								<tr>
									<td colspan="4" class="text-center"
										>NO EXISTE CERTIFICADOS INTERNOS DISPONIBLES</td
									>
								</tr>
							{/if}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
	<div class="col-lg-6 col-xm-12 col-md-12">
		<div class="card">
			<div class="card-header text-center">
				<h4 class="mb-0 display-6">CERTIFICADOS EXTERNOS</h4>
			</div>
			<div class="card-header">
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
						Los certificados externos son aquellas certificaciones que se emiten para tramites fuera
						de la UNEMI tales como cambio de Universidad o tramites públicos.
					</div>
				</div>
			</div>
			<div class="card-body">
				<div class="table-responsive">
					<input
						type="search"
						class="form-control"
						placeholder="Buscar certificado"
						style="width: 100% !important;"
						on:keyup={({ target: { value } }) => searchCertificados(value, 'externo')}
					/>
					<table class="table mb-0 table-hover" style="width: 100%;" id="rwd-table-externo">
						<thead class="table-light">
							<tr>
								<th scope="col" style="" class="border-top-0 text-center">Certificado</th>
								<th scope="col" style="" class="border-top-0 text-center">Código</th>
								<th scope="col" style="" class="border-top-0 text-center">Versión</th>
								<th scope="col" style="" class="border-top-0 text-center">Descargar</th>
							</tr>
						</thead>
						<tbody>
							{#if eCertificadosExternos.length > 0}
								{#each eCertificadosExternos as eCertificado}
									<tr>
										<td class="align-middle certificado_name">
											{eCertificado.certificacion}<br />
											(Tiempo de vigencia de
											{#if eCertificado.tipo_vigencia === 0}
												<span class="badge bg-badge">NINGUNA</span>
											{:else if eCertificado.tipo_vigencia == 1}
												<span class="badge bg-danger">{eCertificado.vigencia} HORAS</span>
											{:else if eCertificado.tipo_vigencia == 2}
												<span class="badge bg-warning text-dark">{eCertificado.vigencia} DÍAS</span>
											{:else if eCertificado.tipo_vigencia == 3}
												<span class="badge bg-success">{eCertificado.vigencia} MESES</span>
											{:else}
												{#if eCertificado.vigencia > 1}
													<span class="badge bg-info text-dark">{eCertificado.vigencia} AÑOS</span>
												{:else}
													<span class="badge bg-info text-dark">{eCertificado.vigencia} AÑO</span>
												{/if}
											{/if})
										</td>
										<td class="align-middle text-center"
											>{eCertificado.codigo}<br />{eCertificado.reporte.codigo}</td
										>
										<td class="align-middle text-center">{eCertificado.version}</td>
										<td class="align-middle text-center">
											<div class="icon-shape icon-lg rounded-3">
												<a  
													href="#{eCertificado.id}"
													on:click|preventDefault={() => action_to_download(eCertificado)}
												>
												<img 
													width="50"
													height="50"
													src={hoveredId === eCertificado.id ? "/assets/images/svg/pdf_download_on.svg" : "/assets/images/svg/pdf_download_off.svg"}
													on:mouseover={() => handleMouseOver(eCertificado.id)}
													on:mouseout={handleMouseOut}
													>
												</a>
											</div>
										</td>
									</tr>
								{/each}
							{:else}
								<tr>
									<td colspan="4" class="text-center"
										>NO EXISTE CERTIFICADOS EXTERNOS DISPONIBLES</td
									>
								</tr>
							{/if}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
</div>

<Modal isOpen={open} {toggle} size="xl">
	<ModalHeader {toggle}>{title_modal}</ModalHeader>
	<ModalBody>
		<object
			data={certificado_url}
			type="application/pdf"
			title="SamplePdf"
			width="500"
			height="720"
		>
			<!--<a href="{certificado_url}">shree</a> -->
		</object>
		<iframe src={certificado_url} width="560" height="315" />
	</ModalBody>
	<ModalFooter>
		<Button color="primary" on:click={toggle}>Cerrar</Button>
	</ModalFooter>
</Modal>

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
