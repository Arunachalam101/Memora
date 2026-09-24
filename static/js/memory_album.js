/**
 * MEMORA Memory Album - Phase 10A
 * Handles Memory Album UI: People, Places, Memories
 */

const MemoryAlbum = {
    currentTab: 'people',
    selectedPatientId: null,
    isCaregiver: false,
    
    // Initialize on page load
    init: function() {
        // Detect if caregiver
        this.isCaregiver = document.body.dataset.userRole === 'caregiver' || 
                          this.checkIfCaregiver();
        
        // Show caregiver section if needed
        if (this.isCaregiver) {
            document.getElementById('caregiver-section').style.display = 'block';
            this.loadPatients();
        } else {
            // For patients: use their own ID
            this.selectedPatientId = document.body.dataset.userId || 
                                    this.getCurrentUserId();
            this.showEditButtons();
            this.loadData('people');
        }
        
        // Setup tab navigation
        document.querySelectorAll('[data-tab]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Setup add buttons
        document.getElementById('add-person-btn').addEventListener('click', 
            () => this.showPersonForm());
        document.getElementById('add-place-btn').addEventListener('click', 
            () => this.showPlaceForm());
        document.getElementById('add-memory-btn').addEventListener('click', 
            () => this.showMemoryForm());
        
        // Setup save buttons
        document.getElementById('save-person-btn').addEventListener('click', 
            () => this.submitPerson());
        document.getElementById('save-place-btn').addEventListener('click', 
            () => this.submitPlace());
        document.getElementById('save-memory-btn').addEventListener('click', 
            () => this.submitMemory());
        
        // Setup edit save buttons
        document.getElementById('save-edit-person-btn').addEventListener('click', 
            () => this.submitEditPerson());
        document.getElementById('save-edit-place-btn').addEventListener('click', 
            () => this.submitEditPlace());
        document.getElementById('save-edit-memory-btn').addEventListener('click', 
            () => this.submitEditMemory());
        
        // Patient selector
        if (this.isCaregiver) {
            document.getElementById('patient-select').addEventListener('change', (e) => {
                this.selectedPatientId = parseInt(e.target.value);
                if (this.selectedPatientId) {
                    this.showEditButtons();
                    this.loadData(this.currentTab);
                }
            });
        }
        
        // Apply translations
        if (typeof I18N !== 'undefined') {
            I18N.applyTranslations();
        }
    },
    
    // Detect if current user is caregiver (from base.html currentUserRole variable)
    checkIfCaregiver: function() {
        if (typeof currentUserRole !== 'undefined') {
            return currentUserRole === 'caregiver';
        }
        const userRole = document.body.getAttribute('data-user-role');
        return userRole === 'caregiver';
    },
    
    // Get current user ID (from base.html currentUserId variable)
    getCurrentUserId: function() {
        if (typeof currentUserId !== 'undefined') {
            return currentUserId;
        }
        return document.body.getAttribute('data-user-id') || 
               localStorage.getItem('userId');
    },
    
    // Load patients for caregiver
    loadPatients: function() {
        fetch('/api/users/patients', { credentials: 'include' })
            .then(r => r.json())
            .then(data => {
                const select = document.getElementById('patient-select');
                select.innerHTML = '<option value="">-- Select Patient --</option>';
                
                if (Array.isArray(data)) {
                    data.forEach(user => {
                        if (user.role === 'patient') {
                            const opt = document.createElement('option');
                            opt.value = user.id;
                            opt.textContent = user.name;
                            select.appendChild(opt);
                        }
                    });
                }
            })
            .catch(err => {
                ErrorHandler.show('Failed to load patients');
                console.error(err);
            });
    },
    
    // Switch between tabs
    switchTab: function(tabName) {
        // Hide all sections
        document.querySelectorAll('.tab-content').forEach(el => {
            el.style.display = 'none';
        });
        
        // Deactivate all buttons
        document.querySelectorAll('[data-tab]').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected section
        document.getElementById(tabName + '-section').style.display = 'block';
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        this.currentTab = tabName;
        this.loadData(tabName);
    },
    
    // Load data for current tab
    loadData: function(tabName) {
        if (!this.selectedPatientId) {
            return;
        }
        
        switch(tabName) {
            case 'people':
                this.loadPeople();
                break;
            case 'places':
                this.loadPlaces();
                break;
            case 'memories':
                this.loadMemories();
                break;
        }
    },
    
    // ========================================
    // LOAD DATA METHODS
    // ========================================
    
    loadPeople: function() {
        fetch(`/api/memory/people?patient_id=${this.selectedPatientId}`, { credentials: 'include' })
            .then(r => r.json())
            .then(data => {
                this.renderPeopleGrid(data);
            })
            .catch(err => {
                ErrorHandler.show('Failed to load people');
                console.error(err);
            });
    },
    
    loadPlaces: function() {
        fetch(`/api/memory/places?patient_id=${this.selectedPatientId}`, { credentials: 'include' })
            .then(r => r.json())
            .then(data => {
                this.renderPlacesGrid(data);
            })
            .catch(err => {
                ErrorHandler.show('Failed to load places');
                console.error(err);
            });
    },
    
    loadMemories: function() {
        fetch(`/api/memory/memories?patient_id=${this.selectedPatientId}`, { credentials: 'include' })
            .then(r => r.json())
            .then(data => {
                this.renderMemoriesGrid(data);
            })
            .catch(err => {
                ErrorHandler.show('Failed to load memories');
                console.error(err);
            });
    },
    
    // ========================================
    // RENDER METHODS
    // ========================================
    
    renderPeopleGrid: function(people) {
        const grid = document.getElementById('people-grid');
        const noPeople = document.getElementById('no-people');
        
        grid.innerHTML = '';
        
        if (people.length === 0) {
            noPeople.style.display = 'block';
            return;
        }
        
        noPeople.style.display = 'none';
        
        people.forEach(person => {
            const card = this.createPersonCard(person);
            grid.appendChild(card);
        });
    },
    
    renderPlacesGrid: function(places) {
        const grid = document.getElementById('places-grid');
        const noPlaces = document.getElementById('no-places');
        
        grid.innerHTML = '';
        
        if (places.length === 0) {
            noPlaces.style.display = 'block';
            return;
        }
        
        noPlaces.style.display = 'none';
        
        places.forEach(place => {
            const card = this.createPlaceCard(place);
            grid.appendChild(card);
        });
    },
    
    renderMemoriesGrid: function(memories) {
        const grid = document.getElementById('memories-grid');
        const noMemories = document.getElementById('no-memories');
        
        grid.innerHTML = '';
        
        if (memories.length === 0) {
            noMemories.style.display = 'block';
            return;
        }
        
        noMemories.style.display = 'none';
        
        memories.forEach(memory => {
            const card = this.createMemoryCard(memory);
            grid.appendChild(card);
        });
    },
    
    // ========================================
    // CARD CREATION METHODS
    // ========================================
    
    createPersonCard: function(person) {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4';
        
        const photoHtml = person.photo ? 
            `<img src="${person.photo}" alt="${person.name}" class="card-img-top" style="height: 200px; object-fit: cover;">` :
            `<div style="height: 200px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #999;">No photo</div>`;
        
        col.innerHTML = `
            <div class="card">
                ${photoHtml}
                <div class="card-body">
                    <h5 class="card-title">${this.escapeHtml(person.name)}</h5>
                    <p class="card-text"><strong>${this.escapeHtml(person.relationship)}</strong></p>
                    ${person.description ? `<p class="card-text text-muted">${this.escapeHtml(person.description)}</p>` : ''}
                </div>
                ${this.isCaregiver ? `
                <div class="card-footer">
                    <button class="btn btn-sm btn-warning" onclick="MemoryAlbum.editPerson(${person.id})">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="MemoryAlbum.deletePerson(${person.id})">Delete</button>
                </div>
                ` : ''}
            </div>
        `;
        
        return col;
    },
    
    createPlaceCard: function(place) {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4';
        
        const photoHtml = place.photo ? 
            `<img src="${place.photo}" alt="${place.name}" class="card-img-top" style="height: 200px; object-fit: cover;">` :
            `<div style="height: 200px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #999;">No photo</div>`;
        
        col.innerHTML = `
            <div class="card">
                ${photoHtml}
                <div class="card-body">
                    <h5 class="card-title">${this.escapeHtml(place.name)}</h5>
                    ${place.description ? `<p class="card-text text-muted">${this.escapeHtml(place.description)}</p>` : ''}
                </div>
                ${this.isCaregiver ? `
                <div class="card-footer">
                    <button class="btn btn-sm btn-warning" onclick="MemoryAlbum.editPlace(${place.id})">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="MemoryAlbum.deletePlace(${place.id})">Delete</button>
                </div>
                ` : ''}
            </div>
        `;
        
        return col;
    },
    
    createMemoryCard: function(memory) {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4';
        
        const photoHtml = memory.photo ? 
            `<img src="${memory.photo}" alt="${memory.title}" class="card-img-top" style="height: 200px; object-fit: cover;">` :
            `<div style="height: 200px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #999;">No photo</div>`;
        
        const dateHtml = memory.memory_date ? 
            `<p class="card-text"><small>${memory.memory_date}</small></p>` : '';
        
        col.innerHTML = `
            <div class="card">
                ${photoHtml}
                <div class="card-body">
                    <h5 class="card-title">${this.escapeHtml(memory.title)}</h5>
                    ${memory.description ? `<p class="card-text text-muted">${this.escapeHtml(memory.description)}</p>` : ''}
                    ${dateHtml}
                </div>
                ${this.isCaregiver ? `
                <div class="card-footer">
                    <button class="btn btn-sm btn-warning" onclick="MemoryAlbum.editMemory(${memory.id})">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="MemoryAlbum.deleteMemory(${memory.id})">Delete</button>
                </div>
                ` : ''}
            </div>
        `;
        
        return col;
    },
    
    // ========================================
    // FORM MODALS
    // ========================================
    
    showPersonForm: function() {
        document.getElementById('personForm').reset();
        document.getElementById('personModalTitle').textContent = 'Add Person';
        this.personModal = new bootstrap.Modal(document.getElementById('personModal'));
        this.personModal.show();
    },
    
    showPlaceForm: function() {
        document.getElementById('placeForm').reset();
        document.getElementById('placeModalTitle').textContent = 'Add Place';
        this.placeModal = new bootstrap.Modal(document.getElementById('placeModal'));
        this.placeModal.show();
    },
    
    showMemoryForm: function() {
        document.getElementById('memoryForm').reset();
        document.getElementById('memoryModalTitle').textContent = 'Add Memory';
        this.memoryModal = new bootstrap.Modal(document.getElementById('memoryModal'));
        this.memoryModal.show();
    },
    
    editPerson: function(personId) {
        // Fetch person data
        fetch(`/api/memory/people?patient_id=${this.selectedPatientId}`, { credentials: 'include' })
            .then(r => r.json())
            .then(people => {
                const person = people.find(p => p.id === personId);
                if (person) {
                    document.getElementById('edit-person-id').value = person.id;
                    document.getElementById('edit-person-name').value = person.name;
                    document.getElementById('edit-person-relationship').value = person.relationship;
                    document.getElementById('edit-person-description').value = person.description || '';
                    
                    this.editPersonModal = new bootstrap.Modal(
                        document.getElementById('editPersonModal')
                    );
                    this.editPersonModal.show();
                }
            });
    },
    
    editPlace: function(placeId) {
        fetch(`/api/memory/places?patient_id=${this.selectedPatientId}`, { credentials: 'include' })
            .then(r => r.json())
            .then(places => {
                const place = places.find(p => p.id === placeId);
                if (place) {
                    document.getElementById('edit-place-id').value = place.id;
                    document.getElementById('edit-place-name').value = place.name;
                    document.getElementById('edit-place-description').value = place.description || '';
                    
                    this.editPlaceModal = new bootstrap.Modal(
                        document.getElementById('editPlaceModal')
                    );
                    this.editPlaceModal.show();
                }
            });
    },
    
    editMemory: function(memoryId) {
        fetch(`/api/memory/memories?patient_id=${this.selectedPatientId}`, { credentials: 'include' })
            .then(r => r.json())
            .then(memories => {
                const memory = memories.find(m => m.id === memoryId);
                if (memory) {
                    document.getElementById('edit-memory-id').value = memory.id;
                    document.getElementById('edit-memory-title').value = memory.title;
                    document.getElementById('edit-memory-description').value = memory.description || '';
                    document.getElementById('edit-memory-date').value = memory.memory_date || '';
                    
                    this.editMemoryModal = new bootstrap.Modal(
                        document.getElementById('editMemoryModal')
                    );
                    this.editMemoryModal.show();
                }
            });
    },
    
    // ========================================
    // SUBMIT METHODS (CREATE/UPDATE)
    // ========================================
    
    submitPerson: function() {
        const name = document.getElementById('person-name').value.trim();
        const relationship = document.getElementById('person-relationship').value.trim();
        const description = document.getElementById('person-description').value.trim();
        const photoFile = document.getElementById('person-photo').files[0];
        
        if (!name || !relationship) {
            ErrorHandler.show('Name and relationship are required');
            return;
        }
        
        const formData = new FormData();
        formData.append('patient_id', this.selectedPatientId);
        formData.append('name', name);
        formData.append('relationship', relationship);
        formData.append('description', description);
        if (photoFile) {
            formData.append('photo', photoFile);
        }
        
        fetch('/api/memory/people', {
            method: 'POST',
            credentials: 'include',
            body: formData
        })
        .then(r => {
            if (r.ok) {
                this.personModal.hide();
                this.loadPeople();
                ErrorHandler.showSuccess('Person added successfully');
            } else {
                return r.json().then(data => {
                    throw new Error(data.error || 'Failed to add person');
                });
            }
        })
        .catch(err => {
            ErrorHandler.show(err.message);
        });
    },
    
    submitPlace: function() {
        const name = document.getElementById('place-name').value.trim();
        const description = document.getElementById('place-description').value.trim();
        const photoFile = document.getElementById('place-photo').files[0];
        
        if (!name) {
            ErrorHandler.show('Place name is required');
            return;
        }
        
        const formData = new FormData();
        formData.append('patient_id', this.selectedPatientId);
        formData.append('name', name);
        formData.append('description', description);
        if (photoFile) {
            formData.append('photo', photoFile);
        }
        
        fetch('/api/memory/places', {
            method: 'POST',
            credentials: 'include',
            body: formData
        })
        .then(r => {
            if (r.ok) {
                this.placeModal.hide();
                this.loadPlaces();
                ErrorHandler.showSuccess('Place added successfully');
            } else {
                return r.json().then(data => {
                    throw new Error(data.error || 'Failed to add place');
                });
            }
        })
        .catch(err => {
            ErrorHandler.show(err.message);
        });
    },
    
    submitMemory: function() {
        const title = document.getElementById('memory-title').value.trim();
        const description = document.getElementById('memory-description').value.trim();
        const memoryDate = document.getElementById('memory-date').value;
        const photoFile = document.getElementById('memory-photo').files[0];
        
        if (!title) {
            ErrorHandler.show('Title is required');
            return;
        }
        
        const formData = new FormData();
        formData.append('patient_id', this.selectedPatientId);
        formData.append('title', title);
        formData.append('description', description);
        if (memoryDate) {
            formData.append('memory_date', memoryDate);
        }
        if (photoFile) {
            formData.append('photo', photoFile);
        }
        
        fetch('/api/memory/memories', {
            method: 'POST',
            credentials: 'include',
            body: formData
        })
        .then(r => {
            if (r.ok) {
                this.memoryModal.hide();
                this.loadMemories();
                ErrorHandler.showSuccess('Memory added successfully');
            } else {
                return r.json().then(data => {
                    throw new Error(data.error || 'Failed to add memory');
                });
            }
        })
        .catch(err => {
            ErrorHandler.show(err.message);
        });
    },
    
    submitEditPerson: function() {
        const personId = parseInt(document.getElementById('edit-person-id').value);
        const name = document.getElementById('edit-person-name').value.trim();
        const relationship = document.getElementById('edit-person-relationship').value.trim();
        const description = document.getElementById('edit-person-description').value.trim();
        const photoFile = document.getElementById('edit-person-photo').files[0];
        
        if (!name || !relationship) {
            ErrorHandler.show('Name and relationship are required');
            return;
        }
        
        const formData = new FormData();
        formData.append('patient_id', this.selectedPatientId);
        formData.append('name', name);
        formData.append('relationship', relationship);
        formData.append('description', description);
        if (photoFile) {
            formData.append('photo', photoFile);
        }
        
        fetch(`/api/memory/people/${personId}`, {
            method: 'PUT',
            credentials: 'include',
            body: formData
        })
        .then(r => {
            if (r.ok) {
                this.editPersonModal.hide();
                this.loadPeople();
                ErrorHandler.showSuccess('Person updated successfully');
            } else {
                return r.json().then(data => {
                    throw new Error(data.error || 'Failed to update person');
                });
            }
        })
        .catch(err => {
            ErrorHandler.show(err.message);
        });
    },
    
    submitEditPlace: function() {
        const placeId = parseInt(document.getElementById('edit-place-id').value);
        const name = document.getElementById('edit-place-name').value.trim();
        const description = document.getElementById('edit-place-description').value.trim();
        const photoFile = document.getElementById('edit-place-photo').files[0];
        
        if (!name) {
            ErrorHandler.show('Place name is required');
            return;
        }
        
        const formData = new FormData();
        formData.append('patient_id', this.selectedPatientId);
        formData.append('name', name);
        formData.append('description', description);
        if (photoFile) {
            formData.append('photo', photoFile);
        }
        
        fetch(`/api/memory/places/${placeId}`, {
            method: 'PUT',
            credentials: 'include',
            body: formData
        })
        .then(r => {
            if (r.ok) {
                this.editPlaceModal.hide();
                this.loadPlaces();
                ErrorHandler.showSuccess('Place updated successfully');
            } else {
                return r.json().then(data => {
                    throw new Error(data.error || 'Failed to update place');
                });
            }
        })
        .catch(err => {
            ErrorHandler.show(err.message);
        });
    },
    
    submitEditMemory: function() {
        const memoryId = parseInt(document.getElementById('edit-memory-id').value);
        const title = document.getElementById('edit-memory-title').value.trim();
        const description = document.getElementById('edit-memory-description').value.trim();
        const memoryDate = document.getElementById('edit-memory-date').value;
        const photoFile = document.getElementById('edit-memory-photo').files[0];
        
        if (!title) {
            ErrorHandler.show('Title is required');
            return;
        }
        
        const formData = new FormData();
        formData.append('patient_id', this.selectedPatientId);
        formData.append('title', title);
        formData.append('description', description);
        if (memoryDate) {
            formData.append('memory_date', memoryDate);
        }
        if (photoFile) {
            formData.append('photo', photoFile);
        }
        
        fetch(`/api/memory/memories/${memoryId}`, {
            method: 'PUT',
            credentials: 'include',
            body: formData
        })
        .then(r => {
            if (r.ok) {
                this.editMemoryModal.hide();
                this.loadMemories();
                ErrorHandler.showSuccess('Memory updated successfully');
            } else {
                return r.json().then(data => {
                    throw new Error(data.error || 'Failed to update memory');
                });
            }
        })
        .catch(err => {
            ErrorHandler.show(err.message);
        });
    },
    
    // ========================================
    // DELETE METHODS
    // ========================================
    
    deletePerson: function(personId) {
        if (confirm('Are you sure you want to delete this person?')) {
            fetch(`/api/memory/people/${personId}?patient_id=${this.selectedPatientId}`, {
                method: 'DELETE',
                credentials: 'include'
            })
            .then(r => {
                if (r.ok) {
                    this.loadPeople();
                    ErrorHandler.showSuccess('Person deleted successfully');
                } else {
                    return r.json().then(data => {
                        throw new Error(data.error || 'Failed to delete person');
                    });
                }
            })
            .catch(err => {
                ErrorHandler.show(err.message);
            });
        }
    },
    
    deletePlace: function(placeId) {
        if (confirm('Are you sure you want to delete this place?')) {
            fetch(`/api/memory/places/${placeId}?patient_id=${this.selectedPatientId}`, {
                method: 'DELETE',
                credentials: 'include'
            })
            .then(r => {
                if (r.ok) {
                    this.loadPlaces();
                    ErrorHandler.showSuccess('Place deleted successfully');
                } else {
                    return r.json().then(data => {
                        throw new Error(data.error || 'Failed to delete place');
                    });
                }
            })
            .catch(err => {
                ErrorHandler.show(err.message);
            });
        }
    },
    
    deleteMemory: function(memoryId) {
        if (confirm('Are you sure you want to delete this memory?')) {
            fetch(`/api/memory/memories/${memoryId}?patient_id=${this.selectedPatientId}`, {
                method: 'DELETE',
                credentials: 'include'
            })
            .then(r => {
                if (r.ok) {
                    this.loadMemories();
                    ErrorHandler.showSuccess('Memory deleted successfully');
                } else {
                    return r.json().then(data => {
                        throw new Error(data.error || 'Failed to delete memory');
                    });
                }
            })
            .catch(err => {
                ErrorHandler.show(err.message);
            });
        }
    },
    
    // ========================================
    // HELPER METHODS
    // ========================================
    
    showEditButtons: function() {
        if (this.isCaregiver) {
            document.getElementById('add-person-btn').style.display = 'inline-block';
            document.getElementById('add-place-btn').style.display = 'inline-block';
            document.getElementById('add-memory-btn').style.display = 'inline-block';
        }
    },
    
    escapeHtml: function(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    MemoryAlbum.init();
});
