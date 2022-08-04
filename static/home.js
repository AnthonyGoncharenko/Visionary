const fileUploader = document.getElementById('file-uploader');
const feedback = document.getElementById('feedback');
const progress = document.getElementById('progress');

const reader = new FileReader();

fileUploader.addEventListener('change', (event) => {
  const files = event.target.files;
  const file = files[0];
  reader.readAsDataURL(file);
  
  reader.addEventListener('progress', (event) => {
    if (event.loaded && event.total) {
      const percent = (event.loaded / event.total) * 100;
      progress.value = percent;
      document.getElementById('progress-label').innerHTML = Math.round(percent) + '%';
      
      if (percent === 100) {
        let msg = `<span style="color:white;">File <u><b>${file.name}</b></u> has been uploaded successfully.</span>`;
        if (files.length > 1) {
            msg = `<span style="color:white;">Files have been uploaded successfully.</span>`;
        }
        feedback.innerHTML = msg;
      }
    }
  });
});