<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentBasicoMedico from './forms/basicos.svelte';
	import ComponentEnfermedad from './forms/enfermedad.svelte';
	import ComponentCovid from './forms/covid.svelte';
	import ComponentContacto from './forms/contacto.svelte';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import { Spinner, Badge, Tooltip } from 'sveltestrap';
	import { converToCapitalizarPrimeraLetra } from '$lib/formats/formatString';
	import Swal from 'sweetalert2';
	import { apiPOST } from '$lib/utils/requestUtils';
	import { addToast } from '$lib/store/toastStore';
	let mOpenModal = false;
	let mTitleModal;
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
	let mSizeModal = 'lg';
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	export let aData;
	let aDataModal;
	let ePersonaExtension = undefined;
	let mTitle = '';
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			ePersonaExtension = aData.ePersonaExtension ?? undefined;
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosPersonalesMedico') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_4');
			menu.click();
		}
	};

	const openModal = (component, title, data) => {
		modalDetalleContent = component;
		mOpenModal = !mOpenModal;
		aDataModal = data;
		mTitleModal = title;
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'md';
	};

	const eliminarRegistro = (body, pk, action) => {
		const mensaje = {
			title: `<p style='color:#FE9900;'><b>Acción irreversible</b></p>`,
			//html: `<p style='color:#ACAEAF;'>¿Desea eliminar familiar ${ePersonaDatosFamiliar.nombre}</p>`,
			html: body,
			customClass: {
				cancelButton: 'btn-mini',
				confirmButton: 'btn-confirm'
			},
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#FE9900',
			//cancelButtonColor: '#d33',
			confirmButtonText: `Si, deseo hacerlo!`,
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire({ ...mensaje }).then(async (result) => {
			if (result.value) {
				loading.setLoading(true, 'Cargando, espere por favor...');
				const [res, errors] = await apiPOST(fetch, 'alumno/hoja_vida', {
					action: action,
					id: pk
				});
				if (errors.length > 0) {
					errors.forEach((element) => {
						addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
					});
				} else {
					if (!res.isSuccess) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					} else {
						addToast({
							type: 'success',
							header: '¡Exitoso!',
							body: res.message
						});
						const menu = document.getElementById('menu_element_4');
						menu.click();
					}
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
			}
		});
	};

	const view_pdf = (url) => {
		aDataModal = { url: url };
		modalDetalleContent = ComponentViewPDF;
		mOpenModal = !mOpenModal;
		mTitleModal = 'Ver pdf';
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'xl';
	};
</script>

{#if ePersonaExtension}
	<!--DATOS BASICOS MEDICOS-->
	<div class="row mb-3">
		<div class="col-12">
			<div class="card h-100">
				<div class="card-header d-sm-flex justify-content-between align-items-center">
					<div class="headtitle  mb-lg-0 m-0">
						<h3 class="mx-2 m-0 p-0">Datos médicos</h3>
						<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
					</div>
					<div>
						<button
							class="btn  btn-sm btn-cian-opacity"
							on:click={() =>
								openModal(ComponentBasicoMedico, 'Editar datos médicos', {
									ePersonaExtension: ePersonaExtension
								})}><i class="fe fe-edit " /> Editar</button
						>
					</div>
				</div>
				<div class="card-body">
					<div class="border-bottom pb-4">
						<div class="row align-items-center g-3 text-center text-sm-start">
							<div class="col-12 col-sm-auto">
								<label class="cursor-pointer avatar avatar-xxl" for="avatarFile"
									><img class="rounded-circle" src={ePersonaExtension.foto_perfil} alt="" />
								</label>
							</div>
							<div class="col-12 col-sm-auto flex-1 px-5">
								<h3 class="mb-4 mt-4">{ePersonaExtension.nombre_completo}</h3>
								<div class="row flex-between-center my-0 ">
									<div class="col-auto ">
										<h5 class="fw-bold">
											{converToCapitalizarPrimeraLetra(ePersonaExtension.tipo_documento)}
										</h5>
									</div>

									<div class="col-auto ">
										<p class="fw-light">{ePersonaExtension.documento}</p>
									</div>
								</div>
								<div class="row flex-between-center my-0">
									<div class="col-auto">
										<h5 class="fw-bold">Email</h5>
									</div>
									<div class="col-auto">
										<a class="lh-1 fw-light" href="mailto:{ePersonaExtension.email_personal}"
											>{ePersonaExtension.email_personal}</a
										>
									</div>
								</div>
							</div>
						</div>
					</div>
					<div class="row g-3 row-cols-1 row-cols-sm-1 row-cols-md-2 row-cols-lg-3 mt-2">
						<div class="col text-center">
							<span class="fs-6 fw-bolder">Tipo de sangre</span>
							{#if ePersonaExtension.tipo_sangre}
								<h4 class="fs-3 mb-0 fw-lighter">{ePersonaExtension.tipo_sangre.sangre}</h4>
							{:else}
								<h4 class="fs-3 mb-0 fw-lighter">S/N</h4>
							{/if}
						</div>
						<div class="col text-center">
							<span class="fs-6 fw-bolder">Peso(Kg)</span>
							<h4 class="fs-3 mb-0 fw-lighter">{ePersonaExtension.peso ?? 'S/N'}</h4>
						</div>
						<div class="col text-center">
							<span class="fs-6 fw-bolder">Estatura(Mts)</span>
							<h4 class="fs-3 mb-0 fw-lighter">
								{ePersonaExtension.talla ?? 'S/N'}
							</h4>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	<div class="row mb-3">
		<div class="col-12 ">
			<div class="card h-100">
				<div class="card-header d-sm-flex justify-content-between align-items-center">
					<div class="headtitle mb-lg-0 m-0">
						<h3 class="mx-2 m-0 p-0">Contacto de emergencia</h3>
					</div>
					<div>
						<button
							class="btn  btn-sm btn-cian-opacity"
							on:click={() =>
								openModal(ComponentContacto, 'Editar contato de emergencia', {
									ePersonaExtension: ePersonaExtension
								})}><i class="fe fe-edit " /> Editar</button
						>
					</div>
				</div>
				<div class="card-body">
					<div class="row g-3 row-cols-1 row-cols-sm-1 row-cols-md-2 row-cols-lg-3">
						<div class="col text-center">
							<span class="fs-6">Nombre:</span>
							<h6 class="mb-0">{ePersonaExtension.contactoemergencia ?? 'S/N'}</h6>
						</div>
						<div class="col text-center">
							<span class="fs-6">Teléfono de emergencia:</span>
							<h6 class="mb-0">{ePersonaExtension.telefonoemergencia ?? 'S/N'}</h6>
						</div>
						<div class="col text-center">
							<span class="fs-6">Parentesco:</span>
							<h6 class="mb-0">
								{#if ePersonaExtension.parentescoemergencia}
									{ePersonaExtension.parentescoemergencia.nombre ?? 'S/N'}
								{:else}
									S/N
								{/if}
							</h6>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	<!--DATOS DE VACUNAS-->
	<div class="row mb-3">
		<div class="col-12 ">
			<div class="card h-100">
				<div class="card-header d-sm-flex justify-content-between align-items-center">
					<div class="headtitle mb-lg-0 m-0">
						<h3 class="mx-2 m-0 p-0">Vacunas COVID-19</h3>
						<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
					</div>
					<div>
						<button
							class="btn btn-success btn-sm "
							on:click={() =>
								openModal(ComponentCovid, 'Adicionar vacunas de COVID-19', {
									eVacuna: undefined
								})}><i class="fe fe-plus " /> Adicionar</button
						>
					</div>
				</div>

				<div class="card-body">
					<div class="table-responsive scrollbar">
						<table class="table table_primary tabla_responsive ">
							<thead class="table-light">
								<tr class="">
									<th
										class="sort white-space-nowrap text-center align-middle "
										scope="col"
										style="width:35%;"
									>
										Información
									</th>
									<th class="sort align-middle text-center" scope="col" style="width:35%;">
										Dosis
									</th>
									<th
										class="sort align-middle white-space-nowrap text-center"
										scope="col"
										style="width:20%;"
									>
										Certificado
									</th>
									<th
										class="sort align-middle white-space-nowrap text-center"
										scope="col"
										style="width:10%;"
									/>
								</tr>
							</thead>
							<tbody class="list">
								{#if ePersonaExtension.vacunas_covid_19.length > 0}
									{#each ePersonaExtension.vacunas_covid_19 as eVacuna}
										<tr class="hover-actions-trigger btn-reveal-trigger position-static">
											<td class="align-middle white-space-nowrap p-1 fs-6">
												<div class="row flex-between-center">
													<div class="col-auto">
														<h5 class="fs-5 mb-0">Recibió:</h5>
													</div>
													<div class="col-auto">
														{#if eVacuna.recibiovacuna}
															<span class="badge bg-success">SI</span>
														{:else}
															<span class="badge bg-danger">NO</span>
														{/if}
													</div>
												</div>
												{#if eVacuna.recibiovacuna}
													<div class="row flex-between-center">
														<div class="col-auto">
															<h5 class="fs-5 mb-0">Tipo Vacuna:</h5>
														</div>
														<div class="col-auto">
															{#if eVacuna.tipovacuna}
																{eVacuna.tipovacuna.nombre ?? ''}
															{:else}
																S/T
															{/if}
														</div>
													</div>
													<div class="row flex-between-center">
														<div class="col-auto">
															<h5 class="fs-5 mb-0">Número de Dosis:</h5>
														</div>
														<div class="col-auto">
															{eVacuna.dosis.length ?? 0}
														</div>
													</div>
													<div class="row flex-between-center">
														<div class="col-auto">
															<h5 class="fs-5 mb-0">Recibió dosis completa:</h5>
														</div>
														<div class="col-auto">
															{#if eVacuna.recibiodosiscompleta}
																<span class="badge bg-success">SI</span>
															{:else}
																<span class="badge bg-danger">NO</span>
															{/if}
														</div>
													</div>
												{:else}
													<div class="row flex-between-center">
														<div class="col-auto">
															<h5 class="fs-5 mb-0">¿Desea ser vacunado?:</h5>
														</div>
														<div class="col-auto">
															{#if eVacuna.deseavacunarse}
																<span class="badge bg-success">SI</span>
															{:else}
																<span class="badge bg-danger">NO</span>
															{/if}
														</div>
													</div>
												{/if}
											</td>
											<td class="status align-middle white-space-nowrap p-1 fs-6">
												{#each eVacuna.dosis as eDosis}
													<div class="row flex-between-center">
														<div class="col-auto">
															<h5 class="fs-5 mb-0">
																Número de dosis: <span class="fs-6 fw-normal"
																	>{eDosis.numdosis}</span
																>
															</h5>
														</div>
														<div class="col-auto">
															<h5 class="fs-5 mb-0">
																Fecha: <span class="fs-6 fw-normal">{eDosis.fechadosis}</span>
															</h5>
														</div>
													</div>
												{/each}
											</td>
											<td class="align-middle text-center white-space-nowrap p-1 fs-6">
												{#if eVacuna.download_certificado}
													<a
														href="javascript:;"
														on:click={() => view_pdf(eVacuna.download_certificado)}
														class="text-danger fs-3"
														id="Tooltip_vacuna_id_{eVacuna.id}"
													>
														<i class="bi bi-file-pdf" />
													</a>
													<Tooltip target="Tooltip_vacuna_id_{eVacuna.id}" placement="top"
														>Ver certificado</Tooltip
													>
												{/if}
											</td>
											<td class="align-middle text-center white-space-nowrap p-1 fs-6">
												<div class="dropdown dropstart">
													<a
														class="btn-icon btn btn-ghost btn-sm rounded-circle "
														href="#"
														role="button"
														id="Dropdown1"
														data-bs-toggle="dropdown"
														aria-haspopup="true"
														aria-expanded="false"
													>
														<i class="fe fe-more-vertical" />
													</a>
													<div class="dropdown-menu" aria-labelledby="Dropdown1" style="">
														<a
															class="dropdown-item"
															href="#editar"
															on:click={() =>
																openModal(ComponentCovid, 'Editar vacunas de COVID-19', {
																	eVacuna: eVacuna
																})}
														>
															<i class="fe fe-edit dropdown-item-icon" />Editar
														</a>

														<a
															class="dropdown-item"
															href="#eliminar"
															on:click={() =>
																eliminarRegistro(
																	`<p style='color:#ACAEAF;'>¿Desea eliminar datos de vacunación del COVID-19</p>`,
																	eVacuna.pk,
																	'deleteDatosMedicoCovid'
																)}
														>
															<i class="fe fe-trash dropdown-item-icon" />Eliminar
														</a>
													</div>
												</div>
											</td>
										</tr>
									{/each}
								{:else}
									<tr class="hover-actions-trigger btn-reveal-trigger position-static">
										<td colspan="4" class="text-center">NO EXISTE REGISTROS DE VACUNAS</td>
									</tr>
								{/if}
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</div>
	</div>
	<!--DATOS DE ENFERMEDADES-->
	<div class="row">
		<div class="col-12 ">
			<div class="card h-100">
				<div class="card-header d-sm-flex justify-content-between align-items-center">
					<div class="headtitle  mb-lg-0 m-0">
						<h3 class="mx-2 m-0 p-0">Enfermedades</h3>
						<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
					</div>
					<div>
						<button
							class="btn btn-success btn-sm "
							on:click={() =>
								openModal(ComponentEnfermedad, 'Agregar enfermedad', {
									ePersonaEnfermedad: undefined
								})}><i class="fe fe-plus " /> Adiconar</button
						>
					</div>
				</div>

				<div class="card-body">
					<div class="table-responsive">
						<table class="table table_primary tabla_responsive">
							<thead class="table-light">
								<tr class="">
									<th
										class="sort white-space-nowrap text-center align-middle "
										scope="col"
										style="width:15%;"
									>
										Tipo
									</th>
									<th
										class="sort white-space-nowrap text-center align-middle "
										scope="col"
										style="width:35%;"
									>
										Enfermedad
									</th>
									<th
										class="sort white-space-nowrap text-center align-middle "
										scope="col"
										style="width:15%;"
									>
										Hereditario
									</th>
									<th
										class="sort align-middle white-space-nowrap text-center"
										scope="col"
										style="width:20%;"
									>
										Archivo Médico
									</th>
									<th
										class="sort align-middle white-space-nowrap text-center"
										scope="col"
										style="width:10%;"
									/>
								</tr>
							</thead>
							<tbody class="list">
								{#if ePersonaExtension.enfermedades.length > 0}
									{#each ePersonaExtension.enfermedades as eEnfermedad}
										<tr class="hover-actions-trigger btn-reveal-trigger position-static fs-6">
											<td class="align-middle white-space-nowrap text-center p-1 fs-6">
												{eEnfermedad.enfermedad.tipo.descripcion}
											</td>
											<td class="status align-middle white-space-nowrap text-center  p-1 fs-6">
												{eEnfermedad.enfermedad.descripcion}
											</td>
											<td class="align-middle text-center white-space-nowrap p-1 fs-6">
												{#if eEnfermedad.enfermedad.hereditaria}
													<span class="badge bg-success">SI</span>
												{:else}
													<span class="badge bg-danger">NO</span>
												{/if}
											</td>
											<td class="align-middle text-center white-space-nowrap p-1 fs-6">
												{#if eEnfermedad.download_archivomedico}
													<a
														href="javascript:;"
														on:click={() => view_pdf(eEnfermedad.download_archivomedico)}
														class="text-danger fs-3"
														id="Tooltip_enfermedad_id_{eEnfermedad.id}"
													>
														<i class="bi bi-file-pdf" />
													</a>
													<Tooltip target="Tooltip_enfermedad_id_{eEnfermedad.id}" placement="top"
														>Ver informe médico</Tooltip
													>
												{/if}
											</td>
											<td class="align-middle text-center white-space-nowrap p-1 fs-6">
												{#if ![2, 5].includes(eEnfermedad.estadoarchivo)}
													<div class="dropdown dropstart">
														<a
															class="btn-icon btn btn-ghost btn-sm rounded-circle"
															href="#"
															role="button"
															id="Dropdown1"
															data-bs-toggle="dropdown"
															aria-haspopup="true"
															aria-expanded="false"
														>
															<i class="fe fe-more-vertical" />
														</a>
														<div class="dropdown-menu" aria-labelledby="Dropdown1" style="">
															<a
																class="dropdown-item"
																href="#editar"
																on:click={() =>
																	openModal(ComponentEnfermedad, 'Editar enfermedad', {
																		ePersonaEnfermedad: eEnfermedad
																	})}
															>
																<i class="fe fe-edit dropdown-item-icon" />Editar
															</a>

															<a
																class="dropdown-item"
																href="#eliminar"
																on:click={() =>
																	eliminarRegistro(
																		`<p style='color:#ACAEAF;'>¿Desea eliminar enfermedad ${eEnfermedad.enfermedad.descripcion}</p>`,
																		eEnfermedad.pk,
																		'deleteDatosMedicoEnfermedad'
																	)}
															>
																<i class="fe fe-trash dropdown-item-icon" />Eliminar
															</a>
														</div>
													</div>
												{/if}
											</td>
										</tr>
									{/each}
								{:else}
									<tr class="hover-actions-trigger btn-reveal-trigger position-static">
										<td colspan="5" class="text-center">NO EXISTE REGISTROS DE ENFERMEDADES</td>
									</tr>
								{/if}
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}

{#if mOpenModal}
	<svelte:component
		this={modalDetalleContent}
		aData={aDataModal}
		{mOpenModal}
		mToggle={mToggleModal}
		mTitle={mTitleModal}
		mClass={mClassModal}
		mSize={mSizeModal}
		on:actionRun={actionRun}
	/>
{/if}
