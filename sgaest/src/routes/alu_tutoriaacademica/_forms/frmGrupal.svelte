<script lang="ts">
	import { apiPOST, apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { customFormErrors } from '$lib/utils/forms';
	export let aData;
	export let mToggle;
	export let mTitle;
	export let mOpenModal;
	export let mClass;
	export let mSize;
	let eSolicitud;
	let inputTextSearch = '';
	const dispatch = createEventDispatcher();
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let eMaterias;
	let eProfesores;
	let eHorarios;
	let eTemas;
	let eEstudiantes;
	let inputObservacion = '';
	let selectProfesor = 0;
	let selectMateria = 0;
	let selectHorario = 0;
	let selectTema = 0;
	let selectTopico = 0;
	let ids = [];
	const eTopicos = [
		{ id: 1, name: 'REFUERZO ACADÉMICO' },
		{ id: 2, name: 'CONSULTAS SOBRE ACTIVIDADES ACADÉMICAS' }
	];
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		eSolicitud = aData.eSolicitud;
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		eMaterias = await loadMaterias();
		mensaje_load = 'Cargando la información, espere por favor...';
		if (eSolicitud) {
			selectMateria = eSolicitud.materiaasignada.materia['pk'] ?? 0;
			eEstudiantes = await loadEstudiantes(selectMateria);
			eProfesores = await loadProfesores(selectMateria);
			selectProfesor = eSolicitud.profesor['pk'] ?? 0;
			eHorarios = await loadHorarios(selectMateria, selectProfesor);
			selectHorario = eSolicitud.horario['pk'] ?? 0;
			selectTopico = eSolicitud.topico ?? 0;
			eTemas = await loadTemas(selectMateria, selectProfesor);
			console.log('eTemas:', eSolicitud.temas);
			if (eSolicitud.temas.length) {
				const eTema = eSolicitud.temas[0];
				selectTema = eTema['tema'] ?? 0;
				console.log('selectTema:', selectTema);
			}

			inputObservacion = eSolicitud.observacion_estudiante ?? '';
		}

		await delay(2000);
		load = false;
	});

	const loadMaterias = async () => {
		return new Promise(async (resolve, reject) => {
			loading.setLoading(true, 'Consultado la información, espere por favor...');
			const [res, errors] = await apiPOST(fetch, 'alumno/tutoria_academica', {
				action: 'loadMaterias'
			});
			if (errors.length > 0) {
				loading.setLoading(false, 'Consultado la información, espere por favor...');
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				reject([]);
			} else {
				if (!res.isSuccess) {
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					addToast({ type: 'error', header: '¡ERROR!', body: res.message });
					if (!res.module_access) {
						goto('/');
					}
					reject([]);
				} else {
					let results = [];
					res.data.results.forEach((element) => {
						results.push({ id: element.id, name: element.name });
					});
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					resolve(results);
				}
			}
		});
	};

	const loadProfesores = async (id) => {
		return new Promise(async (resolve, reject) => {
			loading.setLoading(true, 'Consultado la información, espere por favor...');
			const [res, errors] = await apiPOST(fetch, 'alumno/tutoria_academica', {
				action: 'loadProfesor',
				id: id
			});
			if (errors.length > 0) {
				loading.setLoading(false, 'Consultado la información, espere por favor...');
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				reject([]);
			} else {
				if (!res.isSuccess) {
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					addToast({ type: 'error', header: '¡ERROR!', body: res.message });
					if (!res.module_access) {
						goto('/');
					}
					reject([]);
				} else {
					let results = [];
					res.data.results.forEach((element) => {
						results.push({ id: element.id, name: element.name });
					});
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					resolve(results);
				}
			}
		});
	};

	const loadHorarios = async (idm, idp) => {
		return new Promise(async (resolve, reject) => {
			loading.setLoading(true, 'Consultado la información, espere por favor...');
			const [res, errors] = await apiPOST(fetch, 'alumno/tutoria_academica', {
				action: 'loadHorario',
				idm: idm,
				idp: idp
			});
			if (errors.length > 0) {
				loading.setLoading(false, 'Consultado la información, espere por favor...');
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				reject([]);
			} else {
				if (!res.isSuccess) {
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					addToast({ type: 'error', header: '¡ERROR!', body: res.message });
					if (!res.module_access) {
						goto('/');
					}
					reject([]);
				} else {
					let results = [];
					res.data.results.forEach((element) => {
						results.push({ id: element.id, name: element.name });
					});
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					resolve(results);
				}
			}
		});
	};

	const loadTemas = async (idm, idp) => {
		return new Promise(async (resolve, reject) => {
			loading.setLoading(true, 'Consultado la información, espere por favor...');
			const [res, errors] = await apiPOST(fetch, 'alumno/tutoria_academica', {
				action: 'loadTema',
				idm: idm,
				idp: idp
			});
			if (errors.length > 0) {
				loading.setLoading(false, 'Consultado la información, espere por favor...');
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				reject([]);
			} else {
				if (!res.isSuccess) {
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					addToast({ type: 'error', header: '¡ERROR!', body: res.message });
					if (!res.module_access) {
						goto('/');
					}
					reject([]);
				} else {
					let results = [];
					res.data.results.forEach((element) => {
						results.push({ id: element.id, name: element.name });
					});
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					resolve(results);
				}
			}
		});
	};

	const loadEstudiantes = async (id) => {
		return new Promise(async (resolve, reject) => {
			loading.setLoading(true, 'Consultado la información, espere por favor...');
			const [res, errors] = await apiPOST(fetch, 'alumno/tutoria_academica', {
				action: 'loadEstudiante',
				id: id
			});
			if (errors.length > 0) {
				loading.setLoading(false, 'Consultado la información, espere por favor...');
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				reject([]);
			} else {
				if (!res.isSuccess) {
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					addToast({ type: 'error', header: '¡ERROR!', body: res.message });
					if (!res.module_access) {
						goto('/');
					}
					reject([]);
				} else {
					let results = [];
					res.data.results.forEach((element) => {
						results.push(element);
					});
					loading.setLoading(false, 'Consultado la información, espere por favor...');
					resolve(results);
				}
			}
		});
	};

	const saveSolicitudTutoriaGrupal = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmSolicitud = document.getElementById('frmSolicitud');
		const formData = new FormData($frmSolicitud);
		formData.append('profesor', selectProfesor.toString());
		formData.append('materia', selectMateria.toString());
		formData.append('horario', selectHorario.toString());
		formData.append('topico', selectTopico.toString());
		formData.append('tema', selectTema.toString());
		formData.append('observacion_estudiante', inputObservacion);
		ids = [];
		if (eEstudiantes) {
			eEstudiantes.forEach((eEstudiante) => {
				const checkbox = document.getElementById(`id_input_check_estudiante_${eEstudiante.id}`);
				console.log(checkbox);
				if (checkbox != undefined) {
					if (checkbox.checked) {
						ids.push(eEstudiante.id);
					}
				}
			});
		}
		if (ids.length > 0) {
			formData.append('estudiantes', JSON.stringify(ids));
		}

		if (eSolicitud != undefined) {
			formData.append('id', eSolicitud.pk ?? '0');
		} else {
			formData.append('id', '0');
		}
		formData.append('action', 'saveSolicitudTutoriaGrupal');
		//loading.setLoading(false, 'Guardando la información, espere por favor...');
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/tutoria_academica', formData);
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
				dispatch('actionRun', { action: 'saveSolicitudTutoriaIndividual' });
			}
		}
	};

	const changeMateria = async (event) => {
		const value = event.target.value;
		if (value > 0) {
			eProfesores = await loadProfesores(value);
			eEstudiantes = await loadEstudiantes(value);
		} else {
			eProfesores = undefined;
		}
		eHorarios = undefined;
		eTemas = undefined;
	};

	const changeProfesor = async (event) => {
		const value = event.target.value;
		if (value > 0) {
			eHorarios = await loadHorarios(selectMateria, value);
		} else {
			eHorarios = undefined;
		}
		eTemas = undefined;
	};

	const changeTopico = async (event) => {
		const value = event.target.value;
		if (value > 0) {
			eTemas = await loadTemas(selectMateria, selectProfesor);
		} else {
			eTemas = undefined;
		}
	};

	const searchEstudiante = (text) => {
		// Obtener una referencia a la tabla
		const tabla = document.getElementById('table_estudiantes');
		// Obtener todas las filas de la tabla excepto la primera (encabezados)
		const filas = tabla.getElementsByTagName('tr');
		const searchText = inputTextSearch.toLowerCase();
		for (var i = 1; i < filas.length; i++) {
			var celdas = filas[i].getElementsByTagName('td');
			var found = false;

			for (var j = 0; j < celdas.length; j++) {
				var cellText = celdas[j].textContent.toLowerCase();

				if (cellText.includes(searchText)) {
					found = true;
					break;
				}
			}

			if (found) {
				filas[i].style.display = '';
			} else {
				filas[i].style.display = 'none';
			}
		}
	};

	const actionSearchEstudiante = async () => {
		//console.log(inputTextSearch);
		//eSolicitudes = await loadSolicitudes(inputTextSearch);
		await searchEstudiante(inputTextSearch);
	};

	const actionResetSearchEstudiante = async () => {
		inputTextSearch = '';
		//eSolicitudes = await loadSolicitudes(inputTextSearch);
		await searchEstudiante(inputTextSearch);
	};

	const handleKeyupSearchEstudiante = async (event) => {
		await searchEstudiante(inputTextSearch);
	};

	const changeSeleccionarTodos = (event) => {
		//console.log(event.target.checked);
		const checked = event.target.checked;
		if (eEstudiantes) {
			eEstudiantes.forEach((eEstudiante) => {
				const checkbox = document.getElementById(`id_input_check_estudiante_${eEstudiante.id}`);
				if (checkbox) {
					checkbox.checked = checked;
				}
			});
		}
	};
</script>

{#if mOpenModal}
	<Modal
		isOpen={true}
		toggle={mToggle}
		size={mSize}
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{mTitle}</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmSolicitud">
					<div class="row">
						<div class="col-lg-4 col-12 mb-3">
							<div class="row g-3">
								<div class="col-12">
									<label for="id_materia" class="form-label fw-bold"
										><span><i class="fe fe-alert-octagon text-warning" /></span> Materia:</label
									>
									<select
										class="form-select form-select-sm"
										aria-label=""
										id="id_materia"
										on:change={changeMateria}
										bind:value={selectMateria}
									>
										<option value={0} selected> ----------- </option>
										{#each eMaterias as eMateria}
											{#if selectMateria === eMateria.id}
												<option value={eMateria.id} selected>
													{eMateria.name}
												</option>
											{:else}
												<option value={eMateria.id}>
													{eMateria.name}
												</option>
											{/if}
										{/each}
									</select>

									<div class="valid-feedback" id="id_materia_validate">¡Se ve bien!</div>
								</div>
								{#if selectMateria > 0 && eProfesores}
									<div class="col-12">
										<label for="id_profesor" class="form-label fw-bold"
											><span><i class="fe fe-alert-octagon text-warning" /></span> Profesor:</label
										>
										<select
											class="form-select form-select-sm"
											aria-label=""
											id="id_profesor"
											on:change={changeProfesor}
											bind:value={selectProfesor}
										>
											<option value={0} selected> ----------- </option>
											{#each eProfesores as eProfesor}
												{#if selectProfesor === eProfesor.id}
													<option value={eProfesor.id} selected>
														{eProfesor.name}
													</option>
												{:else}
													<option value={eProfesor.id}>
														{eProfesor.name}
													</option>
												{/if}
											{/each}
										</select>

										<div class="valid-feedback" id="id_profesor_validate">¡Se ve bien!</div>
									</div>
								{/if}
								{#if selectProfesor > 0 && eHorarios}
									<div class="col-12">
										<label for="id_horario" class="form-label fw-bold"
											><span><i class="fe fe-alert-octagon text-warning" /></span> Horario:</label
										>
										<select
											class="form-select form-select-sm"
											aria-label=""
											id="id_horario"
											bind:value={selectHorario}
										>
											<option value={0} selected> ----------- </option>
											{#each eHorarios as eHorario}
												{#if selectHorario === eHorario.id}
													<option value={eHorario.id} selected>
														{eHorario.name}
													</option>
												{:else}
													<option value={eHorario.id}>
														{eHorario.name}
													</option>
												{/if}
											{/each}
										</select>

										<div class="valid-feedback" id="id_horario_validate">¡Se ve bien!</div>
									</div>
								{/if}
								{#if selectHorario > 0 && eTopicos}
									<div class="col-12">
										<label for="id_topico" class="form-label fw-bold"
											><span><i class="fe fe-alert-octagon text-warning" /></span> Tópico:</label
										>
										<select
											class="form-select form-select-sm"
											aria-label=""
											id="id_topico"
											on:change={changeTopico}
											bind:value={selectTopico}
										>
											<option value={0} selected> ----------- </option>
											{#each eTopicos as eTopico}
												{#if selectTopico === eTopico.id}
													<option value={eTopico.id} selected>
														{eTopico.name}
													</option>
												{:else}
													<option value={eTopico.id}>
														{eTopico.name}
													</option>
												{/if}
											{/each}
										</select>

										<div class="valid-feedback" id="id_topico_validate">¡Se ve bien!</div>
									</div>
								{/if}
								{#if selectTopico > 0 && eTemas}
									<div class="col-12">
										<label for="id_tema" class="form-label fw-bold"
											><span><i class="fe fe-alert-octagon text-warning" /></span> Tema:</label
										>
										<select
											class="form-select form-select-sm"
											aria-label=""
											id="id_tema"
											bind:value={selectTema}
										>
											<option value={0} selected> ----------- </option>
											{#each eTemas as eTema}
												{#if selectTema === eTema.id}
													<option value={eTema.id} selected>
														{eTema.name}
													</option>
												{:else}
													<option value={eTema.id}>
														{eTema.name}
													</option>
												{/if}
											{/each}
										</select>

										<div class="valid-feedback" id="id_tema_validate">¡Se ve bien!</div>
									</div>
								{/if}
								{#if selectTema > 0}
									<div class="col-12 ">
										<label for="id_observacion_estudiante" class="form-label fw-bold">
											Observación:</label
										>
										<textarea
											id="id_observacion_estudiante"
											bind:value={inputObservacion}
											class="form-control form-control-sm"
											rows="3"
										/>
										<div class="valid-feedback" id="id_observacion_estudiante_validate">
											¡Se ve bien!
										</div>
									</div>
								{/if}
							</div>
						</div>
						<div class="col-lg-8 col-12">
							<div class="table-responsive scrollbar">
								<h5 class="form-label fw-bold">Estudiantes:</h5>
								{#if eEstudiantes}
									<form class="form-search" on:submit|preventDefault={actionSearchEstudiante}>
										<div class="input-group my-2">
											<input
												type="text"
												class="form-control form-control-sm"
												placeholder="Buscar..."
												aria-label="Buscar..."
												aria-describedby="search"
												on:keyup={handleKeyupSearchEstudiante}
												bind:value={inputTextSearch}
											/>
											<button type="submit" class="btn btn-outline-secondary btn-sm" id="search"
												><i class="fe fe-search " /></button
											>
											{#if inputTextSearch}
												<button
													type="button"
													on:click={actionResetSearchEstudiante}
													class="btn btn-outline-primary btn-sm"
													><i class="fe fe-refresh-ccw " /></button
												>
											{/if}
										</div>
									</form>
								{/if}

								<table class="table table_primary tabla_responsive" id="table_estudiantes">
									<thead class="table-light">
										<tr>
											<th class="text-center align-middle p-1" style="width: 10%;">
												{#if eEstudiantes}
													<input
														class="form-check-input mt-1"
														type="checkbox"
														value=""
														id="id_input_check_estudiante_all"
														on:change={changeSeleccionarTodos}
														aria-label="Checkbox for following text input"
													/>
												{:else}
													<i class="fe fe-settings" />
												{/if}
											</th>
											<th class="text-center align-middle p-1" style="width: 30%;">Documento</th>
											<th class="text-center align-middle p-1" style="width: 70%;">Estudiante</th>
										</tr>
									</thead>
									<tbody>
										{#if eEstudiantes}
											{#each eEstudiantes as eEstudiante}
												<tr>
													<td class="text-center">
														<input
															class="form-check-input mt-0"
															type="checkbox"
															value=""
															id="id_input_check_estudiante_{eEstudiante.id}"
															aria-label="Checkbox for following text input"
														/>
													</td>
													<td class="text-center">{eEstudiante.document}</td>
													<td class="text-left">{eEstudiante.name}</td>
												</tr>
											{/each}
										{:else}
											<tr>
												<td colspan="3" class="text-center">Seleccione la materia y el profesor</td>
											</tr>
										{/if}
									</tbody>
								</table>
							</div>
						</div>
					</div>
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
				<Button color="warning" class="rounded-5 btn-sm" on:click={saveSolicitudTutoriaGrupal}
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
