import { copy } from 'fs-extra';
import { resolve } from 'path';

const copyFiles = async () => {
  const sourcePathBootstrap = resolve('./node_modules/bootstrap/dist/');
  const destPathBootstrap = resolve('./static/bootstrap/');
  const sourcePathSweetAlert2 = resolve('./node_modules/sweetalert2/dist/');
  const destPathSweetAlert2 = resolve('./static/sweetalert2/');


  try {
    await copy(sourcePathBootstrap, destPathBootstrap);
    console.log('Archivos de Bootstrap copiados correctamente');
  } catch (err) {
    console.error("Archivos de Bootstrap error: ",err);
  }
  try {
    await copy(sourcePathSweetAlert2, destPathSweetAlert2);
    console.log('Archivos de SweetAlert2 copiados correctamente');
  } catch (err) {
    console.error("Archivos de SweetAlert2 error: ",err);
  }
};

copyFiles(); 