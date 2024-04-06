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

	let errors: { [inputName: string]: any } = {};

	function isFormValid(data: { [inputName: string]: any }): boolean {
		return !Object.keys(errors).some((inputName) =>
			Object.keys(errors[inputName]).some((errorName) => errors[inputName][errorName])
		);
	}

	function validateForm(data: { [inputName: string]: any }): void {
		if (!isRequiredFieldValid(data.propuesta.name)) {
			errors['propuesta'] = { ...errors['propuesta'], required: true };
		} else {
			errors['propuesta'] = { ...errors['propuesta'], required: false };
		}
	}

	function isRequiredFieldValid(value) {
		return value != null && value !== '';
	}
	const dispatch = createEventDispatcher();

	const save = async (formData) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		formData.append('action', 'adddocensayo');
		formData.append('id',  aData.grupo.id );
		formData.append('es_pareja',  aData.es_pareja );
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

		validateForm(data);
		if (isFormValid(data)) {
			save(formData);
		} else {
			addToast({
				type: 'error',
				header: 'Form invalid',
				body: 'Complete todos los campos correctamente.'
			});
		}
	}

	onMount(async () => {});
</script>

<form id="FormAddDocEnsayo" on:submit|preventDefault={onSubmit}>
	<div class="row">
		<div class="col-12 mb-4" id="fieldset_archivo">
			<FormGroup>
				<Label class="mb-3" for="id_propuesta">Documento Propuesta Ensayo <span class="text-danger">*</span></Label>
				<Input type="file" name="propuesta" id="id_propuesta" />
			</FormGroup>
			{#if errors.propuesta && errors.propuesta.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>

        <div class="col-12 mb-4" id="fieldset_archivo">
			<FormGroup>
				<Label class="mb-3" for="id_extracto">Documento Propuesta Ensayo (Desde introducción hasta conclusión)</Label>
				<Input type="file" name="extracto" id="id_extracto" />
			</FormGroup>
			{#if errors.extracto && errors.extracto.required}
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
