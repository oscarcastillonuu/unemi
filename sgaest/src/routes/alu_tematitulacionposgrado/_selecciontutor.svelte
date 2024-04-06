<script lang="ts">
	export let aData;
	import { browserGet, apiPOST, apiPOSTFormData, apiGET } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import Swal from 'sweetalert2';
	import { addToast } from '$lib/store/toastStore';
	import { addNotification } from '$lib/store/notificationStore';
	import { loading } from '$lib/store/loadingStore';
	import { Badge, Button, Form, FormGroup, Input, FormText, Label } from 'sveltestrap';
	import { createEventDispatcher, onDestroy } from 'svelte';
	const dispatch = createEventDispatcher()
	let errors: { [inputName: string]: any } = {};

	function isFormValid(data: { [inputName: string]: any }): boolean {
		return !Object.keys(errors).some((inputName) =>
			Object.keys(errors[inputName]).some((errorName) => errors[inputName][errorName])
		);
	}

	function validateForm(data: { [inputName: string]: any }): void {
		if (!isRequiredFieldValid(data.obs)) {
			errors['obs'] = { ...errors['obs'], required: true };
		} else {
			errors['obs'] = { ...errors['obs'], required: false };
		}
	}

	function isRequiredFieldValid(value) {
		return value != null && value !== '';
	}
	

	const save = async (formData) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		formData.append('id', aData.tema.id);
		formData.append('action', 'seleccionar_docente_tutor');
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
			console.log('Invalid Form');
		}
	}
</script>

<div class="text-center ">
	{#if aData.tema.profesor.persona.obtenerfoto}
		<!-- content here -->
		<img
			src="{variables.BASE_API}{aData.tema.profesor.persona.obtenerfoto.foto}"
			class="rounded-circle avatar-xl mb-3"
			alt=""
		/>
	{:else if aData.tema.profesor.persona.sexo == 1}
		<!-- content here -->
		<img
			src="{variables.BASE_API_STATIC}/images/iconos/mujer.png"
			class="rounded-circle avatar-xl mb-3"
			alt=""
		/>
	{:else}
		<!-- else content here -->
		<img
			src="{variables.BASE_API_STATIC}/images/iconos/hombre.png"
			class="rounded-circle avatar-xl mb-3"
			alt=""
		/>
	{/if}
	<p class="mb-0">
		{aData.tema.profesor.display}
	</p>
</div>

<form id="FormAprobarRechazarTutor" on:submit|preventDefault={onSubmit}>
	<!-- form -->
	<div class="row">
		<!-- form group -->
		<div class="mb-3 col-12 mt-4">
			<label class="form-label">Observación <span class="text-danger">*</span></label>
			<textarea
				class="form-control"
				name="obs"
				id="obs"
				placeholder="Ingrese alguna observación..."
				rows="4"
			/>
			{#if errors.obs && errors.obs.required}
				<small class="error-message text-danger"
					>campo obligatorio <span class="text-danger">*</span></small
				>
			{/if}
		</div>

		<!-- form group -->
		<div class="mb-3 col-12 mt-4">
			<div class="form-check form-check-inline">
				<input
					class="form-check-input"
					type="radio"
					name="st"
					id="flexRadioDefault1"
					value="1"
					checked
				/>
				<label class="form-check-label" for="flexRadioDefault1"> Aprobar </label>
			</div>
			<div class="form-check form-check-inline">
				<input class="form-check-input" type="radio" name="st" id="flexRadioDefault2" value="2" />
				<label class="form-check-label" for="flexRadioDefault2"> Rechazar</label>
			</div>
		</div>

		<div class="col-md-8" />
		<!-- button -->
		<div class="col-12">
			<button class="btn btn-primary" type="submit">Guardar</button>
		</div>
	</div>
</form>
