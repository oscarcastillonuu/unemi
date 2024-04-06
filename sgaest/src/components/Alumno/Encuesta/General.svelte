<script lang="ts">
	import { variables } from "$lib/utils/constants";
	import { loading } from '$lib/store/loadingStore';

	import { addNotification } from '$lib/store/notificationStore';
	import { addToast } from '$lib/store/toastStore';
	import { onMount } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import { Icon, Button, Modal, ModalBody, ModalFooter, ModalHeader, Form } from 'sveltestrap';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
	import { browserGet, apiPOSTFormData, apiPOST, apiGET } from '$lib/utils/requestUtils';

	export let aData;
	export let mOpen = false;
	export let mToggle;
	export let size = 'md';
	export let es_seguimiento = false;
	let arrayarchivos = [];
	let eFiletablaM = undefined;
	let eEncuenta = {};
	let load = true;
	let idMateria;
	let nombreMateria;
	let respuestas = [];
	const dispatch = createEventDispatcher();
	let pondDocumentoArchivo;
	let nameDocumentoArchivo = 'fileDocumentoArchivo';
	let id_excobligaotorios = []

	onMount(async () => {
		console.log(aData.idMat)
		if (aData.idMat){
			eEncuenta = aData.eQuiz;
			idMateria = aData.idMat;
			nombreMateria = aData.nombreMateria;
		}else {
			eEncuenta = aData;
		}
		load = false;
	});

	const handleInit = () => {
		console.log('FilePond has initialised');
	};
	const handleAddFile = (err, fileItem) => {
		console.log(pondDocumentoArchivo.getFiles());
		console.log('A file has been added', fileItem);
	};

	const validacionradio = (id, tipo) => {
		//const observaionporno = document.getElementById('observaionporno_' + id).value;
		const valorActivo = document.querySelector(
			'input[name=pregunta_tipo_' + tipo + '_' + id + ']:checked'
		).value;
		if (document.getElementById('observaionporno_' + id)) {
			if (valorActivo == 'si') {
				document.getElementById('cls_observaionporno_' + id).style.display = 'none';
			} else {
				document.getElementById('cls_observaionporno_' + id).style.display = 'block';
			}
		}
	};

	const changeRespuestaColor = (id) => {
		const respuesta_pregunta_id = document.getElementById('respuesta_pregunta_id_' + id);
		respuesta_pregunta_id.style.background = '#e7f6d5';
		//respuesta_pregunta_id.style.color = '#689f38';
		respuesta_pregunta_id.style.borderColor = '#689f38';
	};

	const saveEncuesta = async (idMateria = null) => {
		respuestas = [];
		let tieneError = false;
		eEncuenta.preguntas.forEach((ePregunta) => {
			//console.log(ePregunta);

			if (ePregunta.tipo == 1) {
				const radioButtons = document.querySelectorAll(
					'input[name=pregunta_tipo_1_' + ePregunta.id + ']'
				);
				let resp_tipo_1;
				for (const radioButton of radioButtons) {
					if (radioButton.checked) {
						resp_tipo_1 = radioButton.value;
						break;
					}
				}
				if (resp_tipo_1) {
					if (resp_tipo_1 == 'si') {
						respuestas.push({
							id_pregunta: ePregunta.id,
							tipo: ePregunta.tipo,
							respuestas: [
								{
									valor: 1,
									observacion: ''
								}
							]
						});
					} else {
						if (es_seguimiento){
							respuestas.push({
										id_pregunta: ePregunta.id,
										tipo: ePregunta.tipo,
										respuestas: [
											{
												valor: 0,
												observacion: ''
											}
										]
							});
						} else {
							if (document.getElementById('observaionporno_' + ePregunta.id)) {
								if (document.getElementById('observaionporno_' + ePregunta.id).value === '') {
									tieneError = true;
									const respuesta_pregunta_id = document.getElementById(
										'respuesta_pregunta_id_' + ePregunta.id
									);
									respuesta_pregunta_id.style.background = '#ffdde0';
									respuesta_pregunta_id.style.borderColor = '#d32f2f';
								} else {
									respuestas.push({
										id_pregunta: ePregunta.id,
										tipo: ePregunta.tipo,
										respuestas: [
											{
												valor: 0,
												observacion: document.getElementById('observaionporno_' + ePregunta.id).value
											}
										]
									});
								}
							}
						}
					}
				} else {
					if(ePregunta.obligatoria){
						tieneError = true;
						const respuesta_pregunta_id = document.getElementById(
							'respuesta_pregunta_id_' + ePregunta.id
						);
						respuesta_pregunta_id.style.background = '#ffdde0';
						respuesta_pregunta_id.style.borderColor = '#d32f2f';
					}
				}
			}
			if (ePregunta.tipo == 2) {
				const radioButtons = document.querySelectorAll(
					'input[name=pregunta_' + ePregunta.id + '_rango_' + ePregunta.id + ']'
				);
				let resp_tipo_2;
				for (const radioButton of radioButtons) {
					if (radioButton.checked) {
						resp_tipo_2 = radioButton.value;
						break;
					}
				}
				if (resp_tipo_2) {
					respuestas.push({
						id_pregunta: ePregunta.id,
						tipo: ePregunta.tipo,
						respuestas: [
							{
								valor: resp_tipo_2,
								observacion: ''
							}
						]
					});
				} else {
					if(ePregunta.obligatoria){
					tieneError = true;
					const respuesta_pregunta_id = document.getElementById(
						'respuesta_pregunta_id_' + ePregunta.id
					);
					respuesta_pregunta_id.style.background = '#ffdde0';
					respuesta_pregunta_id.style.borderColor = '#d32f2f';
					}
				}
			}
			if (ePregunta.tipo == 3) {
				let resp_tipo_3 = document.getElementById('pregunta_' + ePregunta.id).value;
				if (resp_tipo_3 != '') {
					respuestas.push({
						id_pregunta: ePregunta.id,
						tipo: ePregunta.tipo,
						respuestas: [
							{
								valor: resp_tipo_3,
								observacion: ''
							}
						]
					});
				} else {
					if(ePregunta.obligatoria){
					tieneError = true;
					const respuesta_pregunta_id = document.getElementById(
						'respuesta_pregunta_id_' + ePregunta.id
					);
					respuesta_pregunta_id.style.background = '#ffdde0';
					respuesta_pregunta_id.style.borderColor = '#d32f2f';
					}
				}
			}
			if (ePregunta.tipo == 4) {
				let resp_tipo_4 = document.getElementById('pregunta_' + ePregunta.id).value;
				if (resp_tipo_4 != 0) {
					respuestas.push({
						id_pregunta: ePregunta.id,
						tipo: ePregunta.tipo,
						respuestas: [
							{
								valor: parseInt(resp_tipo_4),
								observacion: ''
							}
						]
					});
				} else {
					if(ePregunta.obligatoria){
					tieneError = true;
					const respuesta_pregunta_id = document.getElementById(
						'respuesta_pregunta_id_' + ePregunta.id
					);
					respuesta_pregunta_id.style.background = '#ffdde0';
					respuesta_pregunta_id.style.borderColor = '#d32f2f';
					}
				}
			}
			if (ePregunta.tipo == 5) {
				let contador_respuesta_tipo_5 = 0;
				let respuestas_5 = [];
				ePregunta.opciones_cuadricula_filas.forEach((element) => {
					const radioButtons = document.querySelectorAll(
						'input[name=pregunta_' + ePregunta.id + '_cuadricula_' + element.id + ']'
					);
					let resp_fila;
					let resp_content = '';

					for (const radioButton of radioButtons) {
						if (radioButton.checked) {
							resp_fila = radioButton.value;
							if (radioButton.getAttribute('esotros') === 'true') {
								console.log('SI');
								resp_content = document.getElementById(
									`respuestaotros_${ePregunta.id}_cuadricula_${element.id}`
								).value;

								if (!resp_content) {
									addNotification({
										msg: 'Debe ingresar una observación',
										type: 'error',
										target: 'newNotificationToast'
									});
									loading.setLoading(false, 'Cargando, espere por favor...');
									tieneError = true;
									return;
								}
							}

							console.log('VA CASI');

							if (radioButton.getAttribute('esarchivo') === 'true') {
								console.log('ENTRO');
								let fileTablaA = pondDocumentoArchivo.getFiles();
								if (fileTablaA.length == 0) {
									addNotification({
										msg: 'Debe subir un archivo',
										type: 'error',
										target: 'newNotificationToast'
									});
									loading.setLoading(false, 'Cargando, espere por favor...');
									return;
								}
								if (fileTablaA.length > 1) {
									addNotification({
										msg: 'Archivo de documento debe ser único',
										type: 'error',
										target: 'newNotificationToast'
									});
									loading.setLoading(false, 'Cargando, espere por favor...');
									return;
								}

								if (pondDocumentoArchivo && pondDocumentoArchivo.getFiles().length > 0) {
									eFiletablaM = pondDocumentoArchivo.getFiles()[0];
									arrayarchivos.push({ id: 'archivo_' + resp_fila, archivo: eFiletablaM.file });
								}
								console.log(eFiletablaM.file);
								// formData.append('eFileTablaAmortizacion', eFiletablaM.file);.
							}
							break;
						}
					}
					if (resp_fila) {
						console.log('ENTRO A LA FILE');
						respuestas_5.push({
							valor: resp_fila,
							observacion: '',
							respuesta: resp_content,
							archivo: 'archivo_' + resp_fila
						});
						contador_respuesta_tipo_5 += 1;
					}
				});

				if (contador_respuesta_tipo_5 < ePregunta.total_opciones_cuadricula_filas) {
					if(ePregunta.obligatoria){
						if(!id_excobligaotorios.includes(ePregunta.id)){
							tieneError = true;
							const respuesta_pregunta_id = document.getElementById(
								'respuesta_pregunta_id_' + ePregunta.id
							);
							respuesta_pregunta_id.style.background = '#ffdde0';
							respuesta_pregunta_id.style.borderColor = '#d32f2f';
						}
					}
				} else {
					respuestas.push({
						id_pregunta: ePregunta.id,
						tipo: ePregunta.tipo,
						respuestas: respuestas_5
					});
				}
			}
			if (ePregunta.tipo == 6) {
				let respuestas_6 = [];
				let contador_respuesta_tipo_6 = 0;
				ePregunta.opciones_multiples.forEach((element) => {
					const radioButtons = document.querySelectorAll(
						'input[name=pregunta_' + ePregunta.id + '_multiple' + element.id + ']'
					);
					let resp_fila;
					let resp_content = '';
					for (const radioButton of radioButtons) {
						if (radioButton.getAttribute('esotros') === 'true' && radioButton.checked) {
							console.log('SI');
							resp_content = document.getElementById(
								`respuestaotros_${ePregunta.id}_opmultiple_${element.id}`
							).value;

							if (!resp_content) {
								addNotification({
									msg: 'Debe ingresar una observación',
									type: 'error',
									target: 'newNotificationToast'
								});
								loading.setLoading(false, 'Cargando, espere por favor...');
								tieneError = true;
								return false;
							}
						}
						if (radioButton.checked) {
							resp_fila = radioButton.value;
							break;
						}
					}
					if (resp_fila) {
						respuestas_6.push({
							valor: resp_fila,
							respuesta: resp_content
						});
						contador_respuesta_tipo_6 += 1;
					}
				});
				if (contador_respuesta_tipo_6 > 0) {
					respuestas.push({
						id_pregunta: ePregunta.id,
						tipo: ePregunta.tipo,
						respuestas: respuestas_6
					});
				} else {
					if(ePregunta.obligatoria){
					tieneError = true;
					const respuesta_pregunta_id = document.getElementById(
						'respuesta_pregunta_id_' + ePregunta.id
					);
					respuesta_pregunta_id.style.background = '#ffdde0';
					respuesta_pregunta_id.style.borderColor = '#d32f2f';
					}
				}
			}
			if (ePregunta.tipo == 7){
				let resp_tipo_7 = document.getElementById('pregunta_' + ePregunta.id).value;
				if (resp_tipo_7 != 0) {
					respuestas.push({
						id_pregunta: ePregunta.id,
						tipo: ePregunta.tipo,
						respuestas: [
							{
								valor: resp_tipo_7,
								observacion: ''
							}
						]
					});
				} else {
					if(ePregunta.obligatoria){
					tieneError = true;
					const respuesta_pregunta_id = document.getElementById(
						'respuesta_pregunta_id_' + ePregunta.id
					);
					respuesta_pregunta_id.style.background = '#ffdde0';
					respuesta_pregunta_id.style.borderColor = '#d32f2f';
					}
				}
			}
		});
		console.log(respuestas);
		if (tieneError) {
			addNotification({
				msg: 'Encuesta incompleta, por favor responder todas las preguntas',
				type: 'error'
			});

			return;
		} else {
			const params = {
				id: eEncuenta.id,
				respuestas: JSON.stringify(respuestas)
			};
			let formdata = new FormData();
			formdata.append('id', eEncuenta.id);
			formdata.append('respuestas', JSON.stringify(respuestas));
			arrayarchivos.forEach((element) => {
				formdata.append(element.id, element.archivo);
			});

			console.log(respuestas);
			loading.setLoading(true, 'Cargando, espere por favor...');
			let ruta = 'alumno/panel/save/quizzes';
			if (es_seguimiento && idMateria){
				formdata.append('idMateria', idMateria);
				ruta = 'alumno/materias/save/quizzes';
			} else {
				ruta = 'alumno/panel/save/quizzes';
			}
			const [res, errors] = await apiPOSTFormData(fetch, ruta, formdata);
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (errors.length > 0) {
				errors.forEach((element) => {
					addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
				});
			} else {
				if (!res.isSuccess) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				} else {
					mOpen = !mOpen;
					addToast({ type: 'success', header: 'Exitoso', body: 'Encuesta guardada correctamente' });
					if (es_seguimiento && idMateria){
						location.reload();
					}
				}
			}
		}
	};
	/*const actionLoadCalendar = () => {
		dispatch('actionRun', {
			action: 'loadCalendar'
		});
	};*/
	const actionEnableInput = (c, f, ePregunta) => {
		var opciones_cuadriculas;
		const element_respothers = document.getElementById(
			`respuestaotros_${ePregunta.id}_cuadricula_${f.id}`
		);
		const element_respothers_archivo = document.getElementById(
			`respuestaarchivo_${ePregunta.id}_cuadricula_${f.id}`
		);
		if(c.secuencia){
			const element_block = document.getElementById(`respuesta_pregunta_id_${c.secuencia}`)
			element_block.style.display = 'block'
			opciones_cuadriculas = eEncuenta.preguntas.map(pre => pre.opciones_cuadricula_columnas.map(ele => ele.pregunta));
			var pregunta = ePregunta.opciones_cuadricula_columnas.map(op => op.secuencia).filter((ele) => ele !== c.secuencia).filter((ele)=> ele !== null).filter((valor, indice, arreglo)=>{return arreglo.indexOf(valor)===indice});
			console.log(pregunta)
			opciones_cuadriculas.reduce((result,lista)=>result.concat(lista)).filter((valor, indice, arreglo)=>{return arreglo.indexOf(valor)===indice}).filter((ele) => ele !== ePregunta.id).filter((ele) => ele !== c.secuencia).forEach(
				ops => {
					const element_select_inputs = document.querySelectorAll(`[name^="pregunta_${ops}_cuadricula_${f.id}"]`)
					element_select_inputs.forEach(radioBtn => {
						radioBtn.checked = false;
					});
					id_excobligaotorios = []
					pregunta.forEach(
							pre => {
								id_excobligaotorios.push(pre)
								const bloques = document.querySelectorAll(`.hiddenblock${pre}`);
								bloques.forEach(bloque => {
									bloque.style.display = 'none';
								});
								console.log(c.secuencia)
								console.log(id_excobligaotorios)
							}
					);
				}
			);
		}
		if(!c.secuencia){
			opciones_cuadriculas = eEncuenta.preguntas.map(pre => pre.opciones_cuadricula_columnas.map(ele => ele.pregunta));
			var opciones_pre = ePregunta.opciones_cuadricula_columnas.map(op => op.secuencia).filter((ele) => ele !== c.secuencia).filter((ele)=> ele !== null).filter((valor, indice, arreglo)=>{return arreglo.indexOf(valor)===indice});
			if(opciones_pre.length > 0){
				opciones_cuadriculas.reduce((result,lista)=>result.concat(lista)).filter((valor, indice, arreglo)=>{return arreglo.indexOf(valor)===indice}).filter((ele) => ele !== ePregunta.id).forEach(
					ops => {
						const element_select_inputs = document.querySelectorAll(`[name^="pregunta_${ops}_cuadricula_"]`)
						element_select_inputs.forEach(radioBtn => {
							radioBtn.checked = false;
						});
						console.log(ops)
						id_excobligaotorios.push(ops)
						const bloques = document.querySelectorAll(`.hiddenblock${ops}`);
						bloques.forEach(bloque => {
							bloque.style.display = 'none';
						});
					}
				);
			}
			console.log(id_excobligaotorios)
		}
		if (c.opcotros) {
			element_respothers.style.display = '';
		} else {
			element_respothers.style.display = 'none';
		}
		if (c.oparchivo) {
			element_respothers_archivo.style.display = '';
		} else {
			element_respothers_archivo.style.display = 'none';
		}
	};
	const actionEnableInputMultiple = (c, ePregunta) => {
		const element_respothers = document.getElementById(
			`respuestaotros_${ePregunta.id}_opmultiple_${c.id}`
		);
		const elementos = document.getElementById(`pregunta_${ePregunta.id}_multiple${c.id}`)
		console.log(elementos);
		if (c.opcotros && elementos.checked) {
			element_respothers.style.display = '';
		} else {
			element_respothers.style.display = 'none';
		}
	};
</script>

{#if !load}
	<Modal
		isOpen={mOpen}
		toggle={mToggle}
		{size}
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
	>
<!--		<ModalHeader>-->
<!--			<h4>-->
<!--				<span>{@html eEncuenta.descripcion}</span>-->
<!--			</h4>-->
<!--			{#if eEncuenta.obligatoria}-->
<!--				<span class="text-info">Encuesta obligatoria</span>-->
<!--			{/if}-->
<!--		</ModalHeader>-->
		<ModalBody class="p-6">
			<div class="row">
				<div class="col-12">
					<div class="headtitle">
						<h3 class="texto-blue">{@html eEncuenta.descripcion}</h3>
						{#if (nombreMateria)}
							<h6 class="fs-6"><b class="fs-6">{'MATERIA: '}</b> {@html nombreMateria}</h6>
						{:else}
							<h6 class="fs-6">{@html eEncuenta.leyenda}</h6>
						{/if}
					</div>
				</div>
			</div>
			<div class="row p-4 py-2">
<!--				<div class="col-12">-->
<!--					<p class="fs-6">-->
<!--						{@html eEncuenta.leyenda}-->
<!--					</p>-->
<!--				</div>-->

				{#each eEncuenta.preguntas as ePregunta, i}
					{#if i >0  && i < eEncuenta.preguntas.length }
						<hr />
					{/if}
					<div
						class="col-12 mb-3 p-3 {ePregunta.es_secuencia?'hiddenblock'+ePregunta.id:''}"
						id="respuesta_pregunta_id_{ePregunta.id}"
						on:change={() => changeRespuestaColor(ePregunta.id)}
						style="display: {ePregunta.es_secuencia?'none':'block'}"
					>
						<h6 class="texto-blue-marin">{i + 1}. {ePregunta.descripcion}</h6>
						<div>
							{#if ePregunta.tipo == 1}
								<div class="form-check form-check-inline">
									<input
										type="radio"
										id="pregunta_{ePregunta.id}_si"
										name="pregunta_tipo_1_{ePregunta.id}"
										class="form-check-input rbt-color"
										value="si"
										on:click={() => validacionradio(ePregunta.id, ePregunta.tipo)}
									/>
									<label class="form-check-label " for="pregunta_{ePregunta.id}_si">Si</label>
								</div>
								<div class="form-check form-check-inline">
									<input
										type="radio"
										id="pregunta_{ePregunta.id}_no"
										name="pregunta_tipo_1_{ePregunta.id}"
										class="form-check-input rbt-color"
										value="no"
										on:click={() => validacionradio(ePregunta.id, ePregunta.tipo)}
									/>
									<label class="form-check-label" for="pregunta_{ePregunta.id}_no">No</label>
								</div>
								{#if !ePregunta.esta_vacia}
									<div id="cls_observaionporno_{ePregunta.id}" style="display: none;">
										<strong>{ePregunta.observacionporno}</strong><br />
										<textarea
											class="form-control"
											id="observaionporno_{ePregunta.id}"
											name="observaionporno_{ePregunta.id}"
											style="width: 100%"
											rows="2"
										/>
									</div>
								{/if}
							{/if}
							{#if ePregunta.tipo == 2}
								{#each ePregunta.rangos as eRango}
									<div class="form-check form-check-inline">
										<input
											type="radio"
											id="pregunta_{ePregunta.id}_rango_{eRango.id}"
											name="pregunta_{ePregunta.id}_rango_{ePregunta.id}"
											class="form-check-input"
											value={eRango.id}
										/>
										<label class="form-check-label " for="pregunta_{ePregunta.id}_rango_{eRango.id}"
											>{eRango.descripcion}</label
										>
									</div>
								{/each}
							{/if}
							{#if ePregunta.tipo == 3}
								<div>
									<textarea
										class="form-control"
										id="pregunta_{ePregunta.id}"
										name="pregunta_{ePregunta.id}"
										style="width: 100%"
										rows="2"
									/>
								</div>
							{/if}
							{#if ePregunta.tipo == 4}
								<div>
									<input
										class="form-control"
										type="number"
										id="pregunta_{ePregunta.id}"
										name="pregunta_{ePregunta.id}"
										value="0"
										min="0"
										max="1000"
										step="1"
									/>
								</div>
							{/if}
							{#if ePregunta.tipo == 5}
								{#if ePregunta.opciones_cuadricula_columnas.length < 7}
									<div class="table-responsive">
										<table class="table table-bordered text-nowrap mb-0">
											<thead>
												<tr>
													<th scope="col" />
													{#each ePregunta.opciones_cuadricula_columnas as c}
														<th
															scope="col"
															class="bg-secondary bg-gradient text-white"
															style="text-align: center"><strong>{c.descripcion}</strong></th
														>
													{/each}
												</tr>
											</thead>
											<tbody>
												{#each ePregunta.opciones_cuadricula_filas as f}
													<tr>
														<td scope="row">{f.descripcion}</td>
														{#each ePregunta.opciones_cuadricula_columnas as c}
															<td style="text-align: center">
																{#if c.oparchivo}
																	<input class="form-check-input"
																		on:change={() => actionEnableInput(c, f, ePregunta)}
																		type="radio"
																		id="pregunta_{ePregunta.id}_cuadricula_{f.id}"
																		name="pregunta_{ePregunta.id}_cuadricula_{f.id}"
																		value={c.id}
																		esarchivo={c.oparchivo}
																	/>
																{:else if c.opcotros}
																	<input class="form-check-input"
																		on:change={() => actionEnableInput(c, f, ePregunta)}
																		type="radio"
																		id="pregunta_{ePregunta.id}_cuadricula_{f.id}"
																		name="pregunta_{ePregunta.id}_cuadricula_{f.id}"
																		value={c.id}
																		esotros={c.opcotros}
																	/>
																{:else}
																	<input class="form-check-input"
																		on:change={() => actionEnableInput(c, f, ePregunta)}
																		type="radio"
																		id="pregunta_{ePregunta.id}_cuadricula_{f.id}"
																		name="pregunta_{ePregunta.id}_cuadricula_{f.id}"
																		value={c.id}
																		esotros={c.opcotros}
																	/>
																{/if}
																{#if c.opcotros}
																	<input
																		id="respuestaotros_{ePregunta.id}_cuadricula_{f.id}"
																		type="text"
																		class="form-control"
																		style="display: none;"
																	/>
																{/if}

																{#if c.oparchivo}
																	<div
																		id="respuestaarchivo_{ePregunta.id}_cuadricula_{f.id}"
																		style="display: none;"
																	>
																		<label
																			for="fileDocumentoArchivo"
																			id="respuestaarchivo_{ePregunta.id}_cuadricula_{f.id}"
																			class="form-label fw-bold"
																		>
																			<i
																				title="Campo obligatorio"
																				class="bi bi-exclamation-circle-fill"
																				style="color: red"
																			/> Subir certificado de COVID-19</label
																		>
																		<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
																		<FilePond
																			class="pb-0 mb-0"
																			id="respuestaarchivo_{ePregunta.id}_cuadricula_{f.id}"
																			bind:this={pondDocumentoArchivo}
																			{nameDocumentoArchivo}
																			name="fileDocumentoArchivo"
																			labelIdle={[
																				'<span class="filepond--label-action">Subir archivo</span>'
																			]}
																			allowMultiple={true}
																			oninit={handleInit}
																			onaddfile={handleAddFile}
																			credits=""
																			acceptedFileTypes={['application/pdf']}
																			labelInvalidField="El campo contiene archivos no válidos"
																			style="display: none;"
																			maxFiles="1"
																			maxParallelUploads="1"
																		/>
																		<small class="text-warning"
																			>Tamaño máximo permitido 15Mb, en formato pdf</small
																		>
																		<!-- <input
																	id="respuestaarchivo_{ePregunta.id}_cuadricula_{f.id}"
																	type="text"
																	class="form-control"
																	style="display: none;"
																	/> -->
																	</div>
																{/if}
															</td>
														{/each}
													</tr>
												{/each}
											</tbody>
										</table>
									</div>
								{:else}
									{#each ePregunta.opciones_cuadricula_filas as f}
										<h6>{f.descripcion}</h6>
										{#each ePregunta.opciones_cuadricula_columnas as c}
											<div class="form-check">
												<input
													on:change={() => actionEnableInput(c, f, ePregunta)}
													class="form-check-input"
													type="radio"
													id="pregunta_{ePregunta.id}_cuadricula_{c.id}"
													name="pregunta_{ePregunta.id}_cuadricula_{f.id}"
													value={c.id}
													esotros={c.opcotros}
												/>
												<label
													class="form-check-label"
													for="pregunta_{ePregunta.id}_cuadricula_{c.id}"
												>
													{c.descripcion}
												</label>
											</div>
										{/each}
									{/each}
								{/if}
							{/if}
							{#if ePregunta.tipo == 6}
								{#each ePregunta.opciones_multiples as mul}
									<div class="form-check">
										{#if mul.opcotros}
										
										<input
											on:change={() => actionEnableInputMultiple(mul, ePregunta)}
											class="form-check-input"
											type="checkbox"
											id="pregunta_{ePregunta.id}_multiple{mul.id}"
											name="pregunta_{ePregunta.id}_multiple{mul.id}"
											value={mul.id}
											esotros={mul.opcotros}
											/>
										<label class="form-check-label" for="pregunta_{ePregunta.id}_multiple{mul.id}"
											>{mul.descripcion}</label
										>
										{:else}
											 <!-- else content here -->
											 <input
											class="form-check-input"
											type="checkbox"
											id="pregunta_{ePregunta.id}_multiple{mul.id}"
											name="pregunta_{ePregunta.id}_multiple{mul.id}"
											value={mul.id}
											esotros={mul.opcotros}
										/>
										<label class="form-check-label" for="pregunta_{ePregunta.id}_multiple{mul.id}"
											>{mul.descripcion}</label
										>
										{/if}
										{#if mul.opcotros}
										<input
											id="respuestaotros_{ePregunta.id}_opmultiple_{mul.id}"
											type="text"
											class="form-control"
											style="display: none;"
										/>
										{/if}
									</div>
								{/each}
							{/if}
							{#if ePregunta.tipo == 7}
							<div>
								<input
									class="form-control"
									type="date"
									id="pregunta_{ePregunta.id}"
									name="pregunta_{ePregunta.id}"
									value="0"
									min="0"
									max="1000"
									step="1"
								/>
							</div>
							{/if}
						</div>
					</div>
				{/each}
			</div>
			<div class="row">
				<div class="col-12 text-center">
					{#if !eEncuenta.obligatoria}
						<Button class="btn-cian-secondary rounded rounded-pill w-15 py-1" on:click={mToggle}>Cerrar</Button>
					{/if}
					<Button class="btn-orange w-15" on:click={() => saveEncuesta(idMateria)}>Guardar</Button>
				</div>
			</div>
		</ModalBody>
<!--		<ModalFooter>-->
<!--			<Button color="success" on:click={() => saveEncuesta()}>Guardar</Button>-->
<!--			{#if !eEncuenta.obligatoria}-->
<!--				<Button color="primary" on:click={mToggle}>Cerrar</Button>-->
<!--			{/if}-->
<!--		</ModalFooter>-->
	</Modal>
{/if}

<style global>
	@import 'filepond/dist/filepond.css';

	.headtitle {
		/*border-radius: 0.25rem;*/
		/* box-shadow: 0 1px 3px rgb(0 0 0 / 12%), 0 1px 2px rgb(0 0 0 / 24%); */
		/*background-color: #fff;*/
		border-left: 4px solid #e9ecef;
		/*margin-bottom: 0rem;*/
		border-left-color: #FE9900;
		/* padding: 1rem; */
		line-height: 21px;
		/*width: 350px;*/
		font-size: 20px;
		margin-bottom: 10px;
		margin-left: 12px;
	}

	.headtitle h3 {
		margin-left: 6px;
		padding-top: 6px;
		margin-bottom: 1px;
		font-weight: bold;
	}

	.headtitle h6 {
		margin-left: 6px;
		margin-bottom: 1px;
		color: #7C7C7C;
	}
	.texto-blue-marin{
		color:#165e97;
		font-weight: bold;
		font-size: 12px;
	}

	.form-check-input:checked[type=radio] {
		background-image:url("./svg/icons/punto.svg") !important;
		background: #FE9900!important;
		border: 0px solid #707070;

	}
	input[type=radio]:checked {
		background-image:url("./svg/icons/punto.svg") !important;
		background: #FE9900!important;
		border: 0px solid #707070;

	}
	input[type=checkbox]:checked{
		background: #FE9900 0% 0% no-repeat padding-box;
		border: 0px solid #707070;
		opacity: 1;
		background-image: none;
	}
	.btn-orange {
		border-radius: 20px;
		/* font-size: 12px; */
		font-weight: 400;
		background-color: #FE9900!important;
		border-color: #FE9900!important;
		color: #fff;
		/* width: 180px; */
		padding: 5px 18px 5px 18px;
	}
	.btn-orange:hover{
		background-color: #FE9900!important;
		border-color: #FE9900!important;
	}
	.btn-cian-secondary {
		background-color: #0d66ae!important;
		color: white!important;
		border-color:#0d66ae;
		/*font-size: 12px;*/
		/*width: 180px;*/
		font-weight: 400;
		border-radius: 20px;
		padding: 5px 18px 5px 18px;
	}

	.btn-cian-secondary:hover {
		background-color: #0d66ae!important;
		border-color:#0d66ae;
		color: white!important;
	}
</style>
