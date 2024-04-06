export const customFormErrors = (form) => {
    const errors = form.errors;
    const fields = form.fields;
    
    fields.forEach((element) => {        
        const field = document.getElementById(`id_${element.field}`);
        const validate = document.getElementById(`id_${element.field}_validate`);
        if (field != undefined) {
            if (field.classList.contains('is-invalid')) {
                field.classList.remove('is-invalid');
            }

            if (field.classList.contains('is-valid')) {
                field.classList.remove('is-valid');
            }
            field.classList.add('is-valid');
            field.style.display = 'block';
        }
        if (validate != undefined) {
            if (validate.classList.contains('valid-feedback')) {
                validate.classList.remove('valid-feedback');
            }

            if (validate.classList.contains('invalid-feedback')) {
                validate.classList.remove('invalid-feedback');
            }
            validate.classList.add('valid-feedback');
            validate.textContent = '¡Se ve bien!';
            validate.style.display = 'block';
        }
    });

    errors.forEach((element) => {
        
        const field = document.getElementById(`id_${element.field}`);
        const validate = document.getElementById(`id_${element.field}_validate`);
        console.log(validate)
        if (field != undefined) {
            if (field.classList.contains('is-invalid')) {
                field.classList.remove('is-invalid');
            }

            if (field.classList.contains('is-valid')) {
                field.classList.remove('is-valid');
            }

            field.classList.add('is-invalid');
        }
        if (validate != undefined) {
            if (validate.classList.contains('valid-feedback')) {
                validate.classList.remove('valid-feedback');
            }

            if (validate.classList.contains('invalid-feedback')) {
                validate.classList.remove('invalid-feedback');
            }

            validate.classList.add('invalid-feedback');
            validate.textContent = element.message;
        }
    });
};


export const resetForms = (display) => {
    const invalid = document.getElementsByClassName('valid-feedback');
    const valid = document.getElementsByClassName('invalid-feedback');
    if (invalid) {
        invalid.forEach((element) => {
            element.style.display = display;
        });
    }
    if (valid) {
        valid.forEach((element) => {
            element.style.display = display;
        });
    }
};