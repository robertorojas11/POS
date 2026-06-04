const DB_NAME = 'apexpos_db';
const DB_VERSION = 2;

export const initDb = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      // Store for caching catalog products
      if (!db.objectStoreNames.contains('products')) {
        db.createObjectStore('products', { keyPath: 'id' });
      }
      
      // Store for caching product categories
      if (!db.objectStoreNames.contains('categories')) {
        db.createObjectStore('categories', { keyPath: 'id' });
      }
      
      // Store for offline checkouts queue
      if (!db.objectStoreNames.contains('sales_queue')) {
        db.createObjectStore('sales_queue', { keyPath: 'id' });
      }

      // Store for discounts
      if (!db.objectStoreNames.contains('discounts')) {
        db.createObjectStore('discounts', { keyPath: 'id' });
      }
    };

    request.onsuccess = (event) => {
      resolve(event.target.result);
    };

    request.onerror = (event) => {
      reject(event.target.error || 'Failed to open database');
    };
  });
};

const getStore = async (storeName, mode = 'readonly') => {
  const db = await initDb();
  const transaction = db.transaction(storeName, mode);
  return transaction.objectStore(storeName);
};

export const dbGet = (storeName, key) => {
  return new Promise(async (resolve, reject) => {
    try {
      const store = await getStore(storeName, 'readonly');
      const request = store.get(key);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    } catch (err) {
      reject(err);
    }
  });
};

export const dbGetAll = (storeName) => {
  return new Promise(async (resolve, reject) => {
    try {
      const store = await getStore(storeName, 'readonly');
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    } catch (err) {
      reject(err);
    }
  });
};

export const dbPut = (storeName, value) => {
  return new Promise(async (resolve, reject) => {
    try {
      const store = await getStore(storeName, 'readwrite');
      const request = store.put(value);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    } catch (err) {
      reject(err);
    }
  });
};

export const dbPutAll = (storeName, values) => {
  return new Promise(async (resolve, reject) => {
    try {
      const db = await initDb();
      const transaction = db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
      
      for (const val of values) {
        store.put(val);
      }
    } catch (err) {
      reject(err);
    }
  });
};

export const dbDelete = (storeName, key) => {
  return new Promise(async (resolve, reject) => {
    try {
      const store = await getStore(storeName, 'readwrite');
      const request = store.delete(key);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    } catch (err) {
      reject(err);
    }
  });
};

export const dbClear = (storeName) => {
  return new Promise(async (resolve, reject) => {
    try {
      const store = await getStore(storeName, 'readwrite');
      const request = store.clear();
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    } catch (err) {
      reject(err);
    }
  });
};
