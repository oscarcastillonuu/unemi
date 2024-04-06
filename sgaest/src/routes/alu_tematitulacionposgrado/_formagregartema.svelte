<script lang="ts">
	export let aData;
	import type { Load } from '@sveltejs/kit';
	import { browserGet, apiPOST, apiPOSTFormData, apiGET } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import Swal from 'sweetalert2';
	import { addToast } from '$lib/store/toastStore';
	import { addNotification } from '$lib/store/notificationStore';
	import { loading } from '$lib/store/loadingStore';
	import { Badge, Button, Form, FormGroup, FormText, Input, Label } from 'sveltestrap';
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Select from 'svelte-select';
	import FormSelectSearch from '$components/Formulario/SelectSearch.svelte';
	import { getMatriculaCompanero } from '$lib/utils/loadDataApi';
	const getOptionLabel = (option) => option.display;
	const getSelectionLabel = (option) => option.display;
	let id = null;
	let convocatorias = [];
	let mecanismos = [];
	let sublineas = [];
	let periodo_id = 0
	let carrera_id = 0
	let selected_mecanismo=0;
	let selected_convocatoria=0;
	let selected_sublinea=0;
	let selected_companero;
	let selectCompaneroMultiples;
	let propuestatema = ''
	let variabledependiente = ''
	let variableindependiente = ''
	let check_pareja = false
	let check_grupal = false
	let moduloreferencia = ''
	let editar = false
	let errors: { [inputName: string]: any } = {};

	function isFormValid(data: { [inputName: string]: any }): boolean {
		return !Object.keys(errors).some((inputName) =>
			Object.keys(errors[inputName]).some((errorName) => errors[inputName][errorName])
		);
	}

	function validateForm(data: { [inputName: string]: any }): void {
		let tiene_companero = document.querySelector('#id_pareja');
		if (tiene_companero.checked) {
			if (data.companero == 0) {
				errors['companero'] = { ...errors['companero'], required: true };
			}else{
				errors['companero'] = { ...errors['companero'], required: false };
			}
		} else {
			errors['companero'] = { ...errors['companero'], required: false };
		}

		if (data.convocatoria == 0) {
			errors['convocatoria'] = { ...errors['convocatoria'], required: true };
		} else {
			errors['convocatoria'] = { ...errors['convocatoria'], required: false };
		}

		if (data.sublinea == 0) {
			errors['sublinea'] = { ...errors['sublinea'], required: true };
		} else {
			errors['sublinea'] = { ...errors['sublinea'], required: false };
		}

		if (data.mecanismotitulacionposgrado == 0) {
			errors['mecanismotitulacionposgrado'] = {
				...errors['mecanismotitulacionposgrado'],
				required: true
			};
		} else {
			errors['mecanismotitulacionposgrado'] = {
				...errors['mecanismotitulacionposgrado'],
				required: false
			};
		}

		if (!isRequiredFieldValid(data.propuestatema)) {
			errors['propuestatema'] = { ...errors['propuestatema'], required: true };
		} else {
			errors['propuestatema'] = { ...errors['propuestatema'], required: false };
		}

		if (data.mecanismotitulacionposgrado == 15 ||data.mecanismotitulacionposgrado == 21) {
			errors['variabledependiente'] = { ...errors['variabledependiente'], required: false };
			errors['variableindependiente'] = { ...errors['variableindependiente'], required: false };
			errors['sublinea'] = { ...errors['sublinea'], required: false };
			errors['archivo'] = { ...errors['archivo'], required: false };
			if (!isRequiredFieldValid(data.moduloreferencia)) {
				errors['moduloreferencia'] = { ...errors['moduloreferencia'], required: true };
			} else {
				errors['moduloreferencia'] = { ...errors['moduloreferencia'], required: false };
			}
		} else {
			errors['moduloreferencia'] = { ...errors['moduloreferencia'], required: false };
			if (!isRequiredFieldValid(data.variabledependiente)) {
				errors['variabledependiente'] = { ...errors['variabledependiente'], required: true };
			} else {
				errors['variabledependiente'] = { ...errors['variabledependiente'], required: false };
			}

			if (!isRequiredFieldValid(data.variableindependiente)) {
				errors['variableindependiente'] = { ...errors['variableindependiente'], required: true };
			} else {
				errors['variableindependiente'] = { ...errors['variableindependiente'], required: false };
			}

			if (!isRequiredFieldValid(data.archivo.name)) {
				errors['archivo'] = { ...errors['archivo'], required: true };
			} else {
				errors['archivo'] = { ...errors['archivo'], required: false };
			}
		}
	}

	function isRequiredFieldValid(value) {
		return value != null && value !== '';
	}
	const dispatch = createEventDispatcher();

	const loadOptions  = async (filterText) => {
		const [res, errors] = await apiGET(fetch, 'alumno/tematitulacion_posgrado', {
			action: 'buscar',
			periodo_id: periodo_id,
			carrera_id: carrera_id,
			filterText: filterText
		});
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
				return new Promise((resolve) => {
					setTimeout(resolve(res.data.items.sort((a, b) => {
          						if (a.display > b.display) return 1;
          						if (a.display < b.display) return -1;
        			})), 2000);
					

				});
				
				
			}
		}
	
	}

	const save = async (formData) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		if (editar) {
			formData.append('action', 'editPropuestaTitulacion');
			formData.append('id', aData.tema.id);
		} else {
			formData.append('action', 'addPropuestaTitulacion');
		}

	
			
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/tematitulacion_posgrado', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				loading.setLoading(false, 'Cargando, espere por favor...');
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
			}
		}
	};

	function onSubmit(e) {
		const formData = new FormData(e.target);

		const data: any = {};
		for (let field of formData) {
			const [key, value] = field;
			data[key] = value;
		}
		if (selected_mecanismo) {
			data['mecanismotitulacionposgrado'] = selected_mecanismo.obtenerid;
		}else{
			data['mecanismotitulacionposgrado'] = 0;
		}
		
		if (selected_convocatoria) {
			data['convocatoria'] = selected_convocatoria.obtenerid;
		}else{
			data['convocatoria'] = 0;
		}

		if (selected_sublinea) {
			data['sublinea'] = selected_sublinea.obtenerid;
		}else{
			data['sublinea'] = 0;
		}

		if (selected_companero) {
			data['companero'] = selected_companero.id;
		}else{
			data['companero'] = 0;
		}
		let ids = [];

		if (selectCompaneroMultiples != null) {
			selectCompaneroMultiples.forEach((element) => {
				ids.push(element.id);
			});

		}
		validateForm(data);
		if (isFormValid(data)) {
			formData.append('mecanismotitulacionposgrado', selected_mecanismo.obtenerid);
			formData.append('convocatoria',  selected_convocatoria.obtenerid);
			formData.append('selectCompaneroMultiples', JSON.stringify(ids));
			if(selected_sublinea == null){
				formData.append('sublinea', '0');
			}else{
				formData.append('sublinea', selected_sublinea.obtenerid);
			}

			formData.append('companero', selected_companero?selected_companero.id:0);
			save(formData);
		} else {
			addToast({ type: 'error', header: 'Form invalid', body: 'Complete todos los campos correctamente.' });
		}
	}

	function mostrar_ocultar_checkbox() {
		let tiene_companero = document.querySelector('#id_pareja');
		let fieldset_companero = document.querySelector('#fieldset_companero');
		if (tiene_companero.checked) {
			fieldset_companero.style.display = 'block';
		} else {
			fieldset_companero.style.display = 'none';
		}
	}
	function mostrar_ocultar_checkbox_grupal() {
			let tiene_companero = document.querySelector('#id_grupal');
			let fieldset_companero = document.querySelector('#fieldset_companeros_grupal');
			if (tiene_companero.checked) {
				fieldset_companero.style.display = 'block';
			} else {
				fieldset_companero.style.display = 'none';
			}
		}

	function mostrar_ocultar_campos_por_mecanismo() {
		let fieldset_variabledependiente = document.querySelector('#fieldset_variabledependiente');
		let fieldset_variableindependiente = document.querySelector('#fieldset_variableindependiente');
		let fieldset_archivo = document.querySelector('#fieldset_archivo');
		let fieldset_moduloreferencia = document.querySelector('#fieldset_moduloreferencia');
		let fieldset_sublineas = document.querySelector('#fieldset_sublineas');
		let fieldset_checkgrupal = document.querySelector('#id_fieldset_check_grupal');
		let fieldset_companero_pareja = document.querySelector('#id_fieldset_companero_check');

		
		if (selected_mecanismo.obtenerid == 15 ||selected_mecanismo.obtenerid == 21) {
			fieldset_variabledependiente.style.display = 'none';
			fieldset_variableindependiente.style.display = 'none';
			fieldset_archivo.style.display = 'none';
			fieldset_moduloreferencia.style.display = 'block';
			fieldset_sublineas.style.display = 'none';
		} else {
			fieldset_variabledependiente.style.display = 'block';
			fieldset_variableindependiente.style.display = 'block';
			fieldset_archivo.style.display = 'block';
			fieldset_moduloreferencia.style.display = 'none';
			fieldset_sublineas.style.display = 'block';
		}
		if (selected_mecanismo.engrupo) {
			fieldset_checkgrupal.style.display = 'block';
			fieldset_companero_pareja.style.display = 'none';

		} else {
			fieldset_checkgrupal.style.display = 'none';
			fieldset_companero_pareja.style.display = 'block';
		}
	}

	onMount(async () => {

		editar = aData.editar
		convocatorias = aData.formImputConvocatoria;
		mecanismos = aData.formImputMecanismoTitulacion;
		sublineas = aData.formImputSublinea;
		periodo_id = aData.periodo_id;
		carrera_id = aData.carrera_id;
		if (editar == true) {
			selected_convocatoria = aData.tema.convocatoria
			selected_sublinea =  aData.tema.sublinea
			selected_mecanismo =  aData.tema.mecanismotitulacionposgrado
			propuestatema = aData.tema.propuestatema 
			variabledependiente = aData.tema.variabledependiente
			variableindependiente = aData.tema.variableindependiente  
			check_pareja = aData.pareja  
			check_grupal = aData.pareja
			moduloreferencia = aData.tema.moduloreferencia
			if (true) {

				selected_companero = []
				if (aData.companero.length > 0) {
					selected_companero = {
						id: aData.companero.matricula['obtenerid'],
						name: aData.companero['display']
					}
					document.getElementById('fieldset_companero').style.display = 'block';
				}


			}

			
		}else{
			document.getElementById('fieldset_companero').style.display='block';
		}
		
		mostrar_ocultar_checkbox();
		mostrar_ocultar_checkbox_grupal();
		mostrar_ocultar_campos_por_mecanismo();

		
	});
</script>

<form id="FormAddPropuestaTitulacion" on:submit|preventDefault={onSubmit}>
	<div class="row">
		<!-- form group -->
		<div class="mb-3 col-12">
			<Label class="form-label" for="id_convocatoria"
				>Convocatoria <span class="text-danger">*</span></Label
			>
			<Select  placeholder="-----------" bind:value={selected_convocatoria} id="id_convocatoria" name="convocatoria" items={convocatorias}  label="display" itemId='id'></Select>
			{#if errors.convocatoria && errors.convocatoria.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>

		<!-- form group -->
		<div class="mb-3 col-12">
			<label class="form-label" for="id_mecanismotitulacionposgrado">
				Mecánismo Titulación <span class="text-danger">*</span></label
			>
		
			<Select placeholder="-----------" bind:value={selected_mecanismo} on:select="{() => mostrar_ocultar_campos_por_mecanismo()}" id="id_mecanismotitulacionposgrado" name="mecanismotitulacionposgrado" items={mecanismos} label="display"  itemId='id'></Select>
			
			{#if errors.mecanismotitulacionposgrado && errors.mecanismotitulacionposgrado.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>

		<!-- form group -->
		<div class="mb-3 col-12" id="fieldset_sublineas">
			<Label class="form-label " for="id_sublinea">
				SubLinea <span class="text-danger">*</span></Label
			>
			<Select  placeholder="-----------" bind:value={selected_sublinea} id="id_sublinea" name="sublinea" items={sublineas} label="display"  itemId='id' ></Select>

			{#if errors.sublinea && errors.sublinea.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>

		<!-- form group -->

		<div class="mb-3 col-12" id="id_fieldset_companero_check">
			<Label class="form-label " for="id_pareja">¿Solo en pareja?</Label>
			<input
				type="checkbox"  checked ={check_pareja}
				on:change={() => mostrar_ocultar_checkbox()}
				id="id_pareja"
				name="pareja"
			/>
		</div>
		<!-- form group -->
		<div class="col-lg-12 col-md-12 col-12 mb-1" id="fieldset_companero">
			<Label class="form-label" for="id_companero">
				Compañero de Titulación <span class="text-danger">*</span></Label
			>
			<FormSelectSearch
								inputId="id_companero"
								name="companero"
								bind:value={selected_companero}
								fetch={(query) => getMatriculaCompanero(query,carrera_id,periodo_id)}
							/>
			{#if errors.companero && errors.companero.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>

		<!-- form group -->


		<div class="mb-3 col-12"id ="id_fieldset_check_grupal">
			<Label class="form-label " for="id_grupal">¿Grupal?</Label>
			<input
				type="checkbox"  checked ={check_grupal}
				on:change={() => mostrar_ocultar_checkbox_grupal()}
				id="id_grupal"
				name="grupal"
			/>

			<div class="col-lg-12 col-md-12 col-12 mb-1" id="fieldset_companeros_grupal">
				<Label class="form-label" for="id_companero">
					Compañero de Titulación <span class="text-danger">*</span></Label
				>
				<FormSelectSearch
						inputId="id_companeros"
						name="companeros"
						bind:value={selectCompaneroMultiples}
						fetch={(query) => getMatriculaCompanero(query,carrera_id,periodo_id)}
						multiple="True"
				/>

				{#if errors.companero && errors.companero.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>

		</div>


		<!-- form group -->
		<div class="mb-3 col-12" id="fieldset_propuestatema">
			<Label class="form-label" for ="id_propuestatema"> Tema <span class="text-danger">*</span></Label>
			<textarea bind:value={propuestatema}
				class="form-control"
				name="propuestatema"
				id="id_propuestatema"
				placeholder="Write here..."
				rows="3"
			/>
			{#if errors.propuestatema && errors.propuestatema.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>
		<!-- form group -->
		<div class="mb-3 col-12" id="fieldset_variabledependiente">
			<Label class="form-label" for="id_variabledependiente">Objetivo General <span class="text-danger">*</span></Label>
			<textarea bind:value={variabledependiente}
				class="form-control"
				id="id_variabledependiente"
				name="variabledependiente"
				placeholder="Write here..."
				rows="3"
			/>
			{#if errors.variabledependiente && errors.variabledependiente.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>

		<!-- form group -->
		<div class="mb-3 col-12" id="fieldset_variableindependiente">
			<Label class="form-label" for="id_variableindependiente">Objetivo Específico <span class="text-danger">*</span></Label>
			<textarea bind:value={variableindependiente}
				class="form-control"
				id="id_variableindependiente"
				name="variableindependiente"
				placeholder="Write here..."
				rows="3"
			/>
			{#if errors.variableindependiente && errors.variableindependiente.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>

		<!-- form group -->
		<div class="mb-3 col-12" id="fieldset_moduloreferencia">
			<Label class="form-label " for="id_moduloreferencia">Módulo de referencia <span class="text-danger">*</span></Label>
			<textarea bind:value={moduloreferencia}
				class="form-control"
				id="id_moduloreferencia"
				name="moduloreferencia"
				placeholder="Write here..."
				rows="3"
			/>
			{#if errors.moduloreferencia && errors.moduloreferencia.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>

		<div class="col-12 mb-4" id="fieldset_archivo">
			<FormGroup>
				<Label class="mb-3" for="id_archivo">Archivo PDF <span class="text-danger">*</span></Label>
				<Input type="file" name="archivo" id="id_archivo" />
			</FormGroup>
			{#if errors.archivo && errors.archivo.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>
		<div class="col-md-8" />
		<div class="col-12 mb-4">
			<button type="submit" class="btn btn-success form-control">Guardar</button>
		</div>
	</div>


	


</form>
