<script lang="ts">
    import { apiPOST, apiPOSTFormData, browserGet, logOutUser } from '$lib/utils/requestUtils';
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import { converToDecimal } from '$lib/formats/formatDecimal';
    let observacion;
	import { loading } from '$lib/store/loadingStore';
	import { addNotification } from '$lib/store/notificationStore';
	import { addToast } from '$lib/store/toastStore';
    const dispatch = createEventDispatcher();
	import { goto } from '$app/navigation';


    const saveInfoPersonal = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoPersonal = document.querySelector('#frmInfoPersonal');
		const formData = new FormData($frmInfoPersonal);
		formData.append('action', 'solicitudeliminacion');


	
        if (!observacion) {
            addNotification({
                msg: 'Favor complete el campo de observación',
                type: 'error',
                target: 'newNotificationToast'
            });
            loading.setLoading(false, 'Cargando, espere por favor...');
            return;
        }
    
        formData.append('observacion', observacion);
		
		
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/complementarias', formData);

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
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
                this.render();
			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};


</script>

<div class="card mb-3 ">
    <form id="frmInfoPersonal" on:submit|preventDefault={saveInfoPersonal}>
        <div class="card-header border-bottom px-4 py-3">
            <h4 class="text-primary">
                <div class="icon-shape icon-lg bg-primary text-white rounded-circle">1</div>
                Información solicitud
            </h4>
        </div>
        <input
            type="text"
            class="form-control"
            id="eObservacion"
            bind:value={observacion}
			/>

            <div class="card-footer text-muted">
				<div class="d-grid gap-2 d-md-flex justify-content-md-end">
					<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
					<button type="submit" class="btn btn-success">Siguiente</button>
				</div>
			</div>
    </form>
</div>
