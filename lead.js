// lead.js - handles display of final report and lead info

function parseRights(report) {
    return report.split('\n').filter(line => /^\d+\./.test(line.trim()));
  }
  
  document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('rightsContainer');
    const report = localStorage.getItem('finalReport') || '';
    const rights = parseRights(report);
  
    rights.forEach(r => {
      const div = document.createElement('div');
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.style.marginLeft = '0.5rem';
      const label = document.createElement('label');
      label.appendChild(checkbox);
      label.append(' ' + r);
      div.appendChild(label);
      container.appendChild(div);
    });
  
    document.getElementById('sendLead').addEventListener('click', () => {
      const name = document.getElementById('leadName').value;
      const phone = document.getElementById('leadPhone').value;
      const email = document.getElementById('leadEmail').value;
      console.log({ name, phone, email });
      alert('תודה! פרטיך התקבלו.');
    });
  });