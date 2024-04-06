<script lang="ts">
	import { element } from 'svelte/internal';
	import FormSelectSearch from '$components/Formulario/SelectSearch.svelte';
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { getTiposVacunaCovid as loadDataTipos } from '$lib/utils/loadDataApi';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';

	export let aData;
	export let mToggle;
	export let mTitle;
	let eVacuna;
	let eTipos;
	let selectTipoVacunaCovid = 0;
	let inputRecibioVacuna = false;
	let inputRecibioDosisCompleta = false;
	let inputDeseaVacunarse = false;
	let eDosis = [];
	let fileCertificado;
	let inputFechaNacimiento = null;
	const dispatch = createEventDispatcher();
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));

	onMount(async () => {
		eVacuna = aData.eVacuna ?? {};
		console.log(eVacuna);
		eTipos = await loadDataTipos();
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		if (eVacuna.tipovacuna) {
			selectTipoVacunaCovid = eVacuna.tipovacuna.pk ?? 0;
		}
		const eDosis_aux = eVacuna.dosis ?? [];
		let contador = 0;
		eDosis_aux.forEach((element) => {
			contador += 1;
			const numdosis = contador;
			element['numdosis'] = numdosis;
			eDosis.push({ ...element });
		});
		inputRecibioVacuna = eVacuna.recibiovacuna ?? false;
		inputRecibioDosisCompleta = eVacuna.recibiodosiscompleta ?? false;
		inputDeseaVacunarse = eVacuna.deseavacunarse ?? false;
		await delay(2000);
		load = false;
	});

	const saveDatosMedicoCovid = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmCovid = document.getElementById('frmCovid');
		const formData = new FormData($frmCovid);
		if (eVacuna != undefined) {
			formData.append('id', eVacuna.pk ?? '0');
		} else {
			formData.append('id', '0');
		}
		formData.append('recibiovacuna', inputRecibioVacuna ? 'true' : 'false');
		formData.append('recibiodosiscompleta', inputRecibioDosisCompleta ? 'true' : 'false');
		formData.append('deseavacunarse', inputDeseaVacunarse ? 'true' : 'false');

		if (selectTipoVacunaCovid != 0) {
			formData.append('tipovacuna', selectTipoVacunaCovid.toString());
		}
		if (fileCertificado) {
			formData.append('certificado', fileCertificado.file);
		}
		if (eDosis.length) {
			formData.append('dosis', JSON.stringify(eDosis));
		}

		formData.append('action', 'saveDatosMedicoCovid');
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/hoja_vida', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (!res.isSuccess) {
				addToast({ type: 'error', header: '¡ERROR!', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				if (res.data.form) {
					await customFormErrors(res.data.form);
				}

				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'saveDatosPersonalesMedico' });
			}
		}
	};

	const handleFileSelectedArchivo = (event) => {
		fileCertificado = event.detail;
	};

	const handleFileRemovedArchivo = () => {
		fileCertificado = null;
	};

	const actionAddDosis = () => {
		eDosis.push({ pk: 0, fechadosis: '', numdosis: eDosis.length + 1 });
		eDosis = [...eDosis];
	};

	const actionDeleteDosis = (numdosis) => {
		let newArr = eDosis.filter((element) => element.numdosis !== numdosis);
		let contador = 0;
		newArr.forEach((element) => {
			contador += 1;
			const numdosis = contador;
			element['numdosis'] = numdosis;
			eDosis.push({ ...element });
		});
		eDosis = [...newArr];
	};

	const actionChangeFecha = (event, numdosis) => {
		let newArr = [];
		eDosis.forEach((element) => {
			if (element['numdosis'] === numdosis) {
				element['fechadosis'] = event.target.value;
			}
			newArr.push({ ...element });
		});
		eDosis = [...newArr];
	};
</script>

{#if eVacuna}
	<Modal
		isOpen={true}
		toggle={mToggle}
		size="lg"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{mTitle}</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmCovid">
					<div class="row g-3">
						<div class="col-12 col-md-6">
							<div class="form-check form-switch">
								<input
									class="form-check-input"
									type="checkbox"
									id="id_recibiovacuna"
									bind:checked={inputRecibioVacuna}
								/>
								<label class="form-check-label fw-bold text-dark" for="id_recibiovacuna"
									>¿Recibió la vacuna contra el COVID-19?</label
								>
							</div>
							<div class="valid-feedback" id="id_recibiovacuna_validate">¡Se ve bien!</div>
						</div>
						{#if inputRecibioVacuna}
							<div class="col-12 col-md-6">
								<div class="form-check form-switch">
									<input
										class="form-check-input"
										type="checkbox"
										id="id_recibiodosiscompleta"
										bind:checked={inputRecibioDosisCompleta}
									/>
									<label class="form-check-label fw-bold text-dark" for="id_recibiodosiscompleta"
										>¿Recibió dosis completa?</label
									>
								</div>
								<div class="valid-feedback" id="id_recibiodosiscompleta_validate">¡Se ve bien!</div>
							</div>
							<div class="col-12">
								<label for="id_tipovacuna" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Tipo de Vacuna:</label
								>
								{#if eTipos}
									<select
										class="form-select form-select-sm"
										aria-label=""
										required
										id="id_tipovacuna"
										bind:value={selectTipoVacunaCovid}
									>
										<option value={0} selected> ----------- </option>
										{#each eTipos as eTipo}
											{#if selectTipoVacunaCovid === eTipo.id}
												<option value={eTipo.id} selected>
													{eTipo.name}
												</option>
											{:else}
												<option value={eTipo.id}>
													{eTipo.name}
												</option>
											{/if}
										{/each}
									</select>
								{/if}
								<div class="valid-feedback" id="id_tipovacuna_validate">¡Se ve bien!</div>
							</div>
						{:else}
							<div class="col-12">
								<div class="form-check form-switch">
									<input
										class="form-check-input"
										type="checkbox"
										id="id_deseavacunarse"
										bind:checked={inputDeseaVacunarse}
									/>
									<label class="form-check-label fw-bold text-dark" for="id_deseavacunarse"
										>¿Desea ser vacunado?</label
									>
								</div>
								<div class="valid-feedback" id="id_deseavacunarse_validate">¡Se ve bien!</div>
							</div>
						{/if}
					</div>
					{#if inputRecibioVacuna}
						<hr />
						<h3 class="fw-bold text-primary">Dosis</h3>
						<div class="row g-3">
							<div class="col-12">
								<table class="table table-bordered table-striped table-condensed fs-6">
									<thead>
										<tr>
											<th style="text-align: center; width: 40%;"> Número de Dosis </th>
											<th style="text-align: center; width: 40%;"> Fecha </th>
											<th style="text-align: center; width: 20%;">
												<button
													type="button"
													on:click={() => actionAddDosis()}
													class="btn btn-primary btn-sm text-white p-1 m-0"
													style="text-shadow: 0 -1px 0 rgba(0, 0, 0, 0.25);
                                                    background-color: #006dcc;     border-color: rgba(0, 0, 0, 0.15) rgba(0, 0, 0, 0.15) rgba(0, 0, 0, 0.25);"
												>
													<i class="fe fe-plus" /></button
												>
											</th>
										</tr>
									</thead>
									<tbody id="tbDetalleDosis">
										{#each eDosis as eDosi}
											<tr>
												<td class="text-center align-middle">{eDosi.numdosis}</td>
												<td class="text-center align-middle">
													<input
														type="date"
														class="form-control form-control-sm"
														placeholder="Seleccione una fecha..."
														data-input
														pattern="(?:19|20)\[0-9\]{2}-(?:(?:0\[1-9\]|1\[0-2\])/(?:0\[1-9\]|1\[0-9\]|2\[0-9\])|(?:(?!02)(?:0\[1-9\]|1\[0-2\])/(?:30))|(?:(?:0\[13578\]|1\[02\])-31))"
														value={eDosi.fechadosis}
														id="id_fechadosis_{eDosi.numdosis}"
														on:change={(event) => actionChangeFecha(event, eDosi.numdosis)}
													/>
												</td>
												<td class="text-center align-middle">
													<button
														type="button"
														class="btn btn-danger m-0 p-1"
														on:click={() => actionDeleteDosis(eDosi.numdosis)}
														><i class="fe fe-trash " /></button
													>
												</td>
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						</div>
						<hr />
						<h3 class="fw-bold text-primary">Archivos</h3>
						<div class="row g-3">
							<div class="col-12">
								<label for="id_certificado" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Certificado:</label
								>
								{#if eVacuna.estadoarchivo != 2}
									<FileUploader
										inputID="id_certificado"
										inputName="certificado"
										acceptedFileTypes={['application/pdf']}
										labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
										on:fileSelected={handleFileSelectedArchivo}
										on:fileRemoved={handleFileRemovedArchivo}
									/>
									<div class="text-center fs-6">
										<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small
										>
									</div>
								{/if}
								{#if eVacuna.download_certificado}
									<div class="fs-6">
										Tienes un archivo subido:
										<a
											title="Ver archivo"
											href={eVacuna.download_certificado}
											target="_blank"
											class="text-primary text-center">Ver archivo</a
										>
									</div>
								{/if}

								<div class="valid-feedback" id="id_certificado_validate">¡Se ve bien!</div>
							</div>
						</div>
					{/if}
				</form>
			{:else}
				<div class="m-0 my-5 justify-content-center align-items-center">
					<div class="text-center align-middle">
						<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
						<h3>{mensaje_load}</h3>
					</div>
				</div>
			{/if}
		</ModalBody>
		<ModalFooter>
			{#if !load}
				<Button color="warning" class="rounded-5 btn-sm" on:click={saveDatosMedicoCovid}
					><i class="fe fe-check" /> Guardar</Button
				>
			{/if}
			<Button color="secondary" class="rounded-5 btn-sm " on:click={mToggle}
				><i class="fe fe-x" /> Cancelar</Button
			>
		</ModalFooter>
	</Modal>
{/if}

<style>
	.form-select {
		border-color: #aaa;
	}
	.form-control {
		border-color: #aaa;
	}
</style>
